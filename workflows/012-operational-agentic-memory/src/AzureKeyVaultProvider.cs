using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;
using Microsoft.Extensions.Logging;

namespace PPA.Secrets;

/// <summary>
/// Resolves secrets from Azure Key Vault using <see cref="DefaultAzureCredential"/>.
/// Translates canonical names to AKV's double-dash path convention.
/// </summary>
/// <remarks>
/// AKV does not allow forward slashes in secret names. The canonical form
/// {BOT_NAME}__{APP_NAME}__{KEY_NAME} is mapped to {bot-name}--{app-name}--{key-name}
/// (lowercase, double-dash separated).
///
/// Authentication order via DefaultAzureCredential:
///   Production:  Entra Managed Identity (no static credentials)
///   CI:          Federated OIDC service principal
///   Local dev:   'az login' interactive session
/// This matches the spec's Short-lived credentials principle (Section 3.2).
/// </remarks>
public sealed class AzureKeyVaultProvider : ISecretsProvider
{
    private readonly SecretClient _client;
    private readonly ILogger<AzureKeyVaultProvider> _logger;

    /// <param name="vaultUri">
    /// The URI of the Azure Key Vault instance (e.g. "https://ppa-secrets.vault.azure.net/").
    /// </param>
    /// <param name="logger">Logger — must never log secret values, only key names.</param>
    public AzureKeyVaultProvider(Uri vaultUri, ILogger<AzureKeyVaultProvider> logger)
    {
        _client = new SecretClient(vaultUri, new DefaultAzureCredential());
        _logger = logger;
    }

    /// <inheritdoc/>
    public async Task<string?> GetAsync(
        string botId,
        string canonicalKey,
        CancellationToken cancellationToken = default)
    {
        var akvName = ToAkvName(canonicalKey);
        _logger.LogDebug("AKV get: bot={BotId} key={CanonicalKey} akvName={AkvName}", botId, canonicalKey, akvName);

        try
        {
            var response = await _client.GetSecretAsync(akvName, cancellationToken: cancellationToken);
            return response.Value.Value;
        }
        catch (Azure.RequestFailedException ex) when (ex.Status == 404)
        {
            _logger.LogDebug("AKV: secret not found — bot={BotId} key={CanonicalKey}", botId, canonicalKey);
            return null;
        }
    }

    /// <inheritdoc/>
    public async Task<SecretBundle> GetBundleAsync(
        string botId,
        IReadOnlyList<SecretDescriptor> descriptors,
        TimeSpan ttl,
        CancellationToken cancellationToken = default)
    {
        var secrets = new Dictionary<string, string>();
        var issuedAt = DateTimeOffset.UtcNow;

        foreach (var descriptor in descriptors)
        {
            var canonicalKey = SecretNameTranslator.ToCanonical(botId, descriptor.AppName, descriptor.CanonicalKey);

            if (IsBlocked(canonicalKey, descriptors))
                throw new SecretBlockedException(botId, canonicalKey);

            var value = await GetAsync(botId, canonicalKey, cancellationToken);

            if (value is not null)
            {
                secrets[canonicalKey] = value;
            }
            else if (descriptor.Required)
            {
                throw new SecretNotFoundException(botId, canonicalKey);
            }
            else
            {
                _logger.LogDebug("AKV: optional secret not found, skipping — bot={BotId} key={CanonicalKey}", botId, canonicalKey);
            }
        }

        return new SecretBundle(botId, secrets, issuedAt, issuedAt.Add(ttl));
    }

    /// <inheritdoc/>
    public Task<SecretBundle> RefreshAsync(
        SecretBundle expiredBundle,
        IReadOnlyList<SecretDescriptor> descriptors,
        TimeSpan ttl,
        CancellationToken cancellationToken = default)
        => GetBundleAsync(expiredBundle.BotId, descriptors, ttl, cancellationToken);

    /// <summary>
    /// Translates a canonical key name to AKV format.
    /// Canonical: LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
    /// AKV:       legal-bot--westlaw--westlaw-api-key
    /// </summary>
    internal static string ToAkvName(string canonicalKey)
        => canonicalKey.Replace("__", "--").Replace("_", "-").ToLowerInvariant();

    private static bool IsBlocked(string canonicalKey, IReadOnlyList<SecretDescriptor> descriptors)
    {
        foreach (var d in descriptors)
        {
            foreach (var blocked in d.Blocked)
            {
                if (string.Equals(blocked, canonicalKey, StringComparison.OrdinalIgnoreCase))
                    return true;
            }
        }
        return false;
    }
}
