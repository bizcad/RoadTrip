using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace PPA.Secrets;

/// <summary>
/// Resolves secrets using a primary vault with automatic fallback to a secondary vault.
/// Logs which vault served each request for telemetry and audit purposes.
/// </summary>
/// <remarks>
/// Implements the dual-vault resilience pattern:
///   Dev:   HashiCorp Vault OSS (primary) → UserSecrets (fallback)
///   CI:    Environment variables (primary) → Azure Key Vault (fallback)
///   Prod:  Azure Key Vault (primary) → HashiCorp Vault OSS (fallback)
///
/// The agent calling this provider does not know or care which vault answered.
/// The abstraction absorbs the routing decision, consistent with unified-auth-spec-v0.2
/// Section 3.2: no ambient authority, but transparent to the consumer.
///
/// Telemetry: every Get and GetBundle call records which provider responded.
/// This feeds the Evaluate phase of SRCGEEE for monitoring vault health.
/// </remarks>
public sealed class CompositeSecretsProvider : ISecretsProvider
{
    private readonly ISecretsProvider _primary;
    private readonly ISecretsProvider _fallback;
    private readonly ILogger<CompositeSecretsProvider> _logger;

    /// <param name="primary">Primary vault to try first.</param>
    /// <param name="fallback">Fallback vault used when primary fails or returns null.</param>
    /// <param name="logger">Logger for vault-selection telemetry (no secret values).</param>
    public CompositeSecretsProvider(
        ISecretsProvider primary,
        ISecretsProvider fallback,
        ILogger<CompositeSecretsProvider> logger)
    {
        _primary = primary;
        _fallback = fallback;
        _logger = logger;
    }

    /// <inheritdoc/>
    /// <remarks>
    /// Tries primary first. Falls back only when primary returns null or throws a transient error.
    /// <see cref="SecretBlockedException"/> propagates immediately without fallback — a block is intentional policy.
    /// </remarks>
    public async Task<string?> GetAsync(
        string botId,
        string canonicalKey,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var value = await _primary.GetAsync(botId, canonicalKey, cancellationToken);
            if (value is not null)
            {
                _logger.LogDebug("Composite: served by PRIMARY — bot={BotId} key={Key}", botId, canonicalKey);
                return value;
            }
        }
        catch (SecretBlockedException)
        {
            // Block decisions are policy, not transient errors — do not attempt fallback.
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex,
                "Composite: PRIMARY failed, attempting fallback — bot={BotId} key={Key} error={Error}",
                botId, canonicalKey, ex.Message);
        }

        // Primary returned null or threw — try fallback
        _logger.LogDebug("Composite: attempting FALLBACK — bot={BotId} key={Key}", botId, canonicalKey);
        var fallbackValue = await _fallback.GetAsync(botId, canonicalKey, cancellationToken);

        if (fallbackValue is not null)
            _logger.LogInformation("Composite: served by FALLBACK — bot={BotId} key={Key}", botId, canonicalKey);
        else
            _logger.LogDebug("Composite: not found in either vault — bot={BotId} key={Key}", botId, canonicalKey);

        return fallbackValue;
    }

    /// <inheritdoc/>
    /// <remarks>
    /// Attempts to build the full bundle from primary. On any failure, retries entirely from fallback.
    /// Bundle TTL is respected: the returned bundle carries the issued/expires timestamps from
    /// whichever provider succeeded.
    /// </remarks>
    public async Task<SecretBundle> GetBundleAsync(
        string botId,
        IReadOnlyList<SecretDescriptor> descriptors,
        TimeSpan ttl,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var bundle = await _primary.GetBundleAsync(botId, descriptors, ttl, cancellationToken);
            _logger.LogInformation(
                "Composite: bundle resolved from PRIMARY — bot={BotId} count={Count} expires={Expires}",
                botId, bundle.Secrets.Count, bundle.ExpiresAt);
            return bundle;
        }
        catch (SecretBlockedException)
        {
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex,
                "Composite: PRIMARY bundle failed, attempting FALLBACK — bot={BotId} error={Error}",
                botId, ex.Message);
        }

        var fallbackBundle = await _fallback.GetBundleAsync(botId, descriptors, ttl, cancellationToken);
        _logger.LogInformation(
            "Composite: bundle resolved from FALLBACK — bot={BotId} count={Count} expires={Expires}",
            botId, fallbackBundle.Secrets.Count, fallbackBundle.ExpiresAt);
        return fallbackBundle;
    }

    /// <inheritdoc/>
    public async Task<SecretBundle> RefreshAsync(
        SecretBundle expiredBundle,
        IReadOnlyList<SecretDescriptor> descriptors,
        TimeSpan ttl,
        CancellationToken cancellationToken = default)
    {
        _logger.LogDebug("Composite: refreshing expired bundle — bot={BotId} expiredAt={Expiry}",
            expiredBundle.BotId, expiredBundle.ExpiresAt);
        return await GetBundleAsync(expiredBundle.BotId, descriptors, ttl, cancellationToken);
    }
}
