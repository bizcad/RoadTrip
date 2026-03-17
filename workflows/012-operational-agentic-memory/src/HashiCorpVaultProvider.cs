using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace PPA.Secrets;

/// <summary>
/// Resolves secrets from a self-hosted HashiCorp Vault OSS instance using AppRole authentication.
/// Translates canonical names to Vault's forward-slash path convention.
/// </summary>
/// <remarks>
/// Phase 1 uses AppRole auth: each agent type has a Role ID baked into its definition,
/// and a short-lived Secret ID is generated at spawn time. This is the direct migration
/// path from <c>config/auth.yaml</c> described in unified-auth-spec-v0.2 Open Question #6.
///
/// Phase 3b hook: When SPIFFE/SPIRE is available, swap AppRole for the Vault JWT auth method,
/// presenting the agent's SPIFFE SVID. The <see cref="ISecretsProvider"/> interface is unchanged.
///
/// Canonical-to-Vault path translation:
///   Canonical:  LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
///   Vault path: secret/legal-bot/westlaw/WESTLAW_API_KEY
/// </remarks>
public sealed class HashiCorpVaultProvider : ISecretsProvider
{
    private readonly HttpClient _http;
    private readonly string _mountPath;
    private readonly ILogger<HashiCorpVaultProvider> _logger;
    private readonly HashiCorpVaultOptions _options;
    private string? _vaultToken;
    private DateTimeOffset _tokenExpiry = DateTimeOffset.MinValue;

    public HashiCorpVaultProvider(
        HashiCorpVaultOptions options,
        ILogger<HashiCorpVaultProvider> logger)
    {
        _options = options;
        _mountPath = options.MountPath ?? "secret";
        _logger = logger;
        _http = new HttpClient { BaseAddress = new Uri(options.VaultAddress) };
    }

    /// <inheritdoc/>
    public async Task<string?> GetAsync(
        string botId,
        string canonicalKey,
        CancellationToken cancellationToken = default)
    {
        await EnsureAuthenticatedAsync(cancellationToken);

        var vaultPath = ToVaultPath(canonicalKey);
        _logger.LogDebug("Vault get: bot={BotId} key={CanonicalKey} path={VaultPath}", botId, canonicalKey, vaultPath);

        using var request = new HttpRequestMessage(HttpMethod.Get, $"/v1/{_mountPath}/data/{vaultPath}");
        request.Headers.Add("X-Vault-Token", _vaultToken);

        using var response = await _http.SendAsync(request, cancellationToken);

        if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
        {
            _logger.LogDebug("Vault: secret not found — bot={BotId} key={CanonicalKey}", botId, canonicalKey);
            return null;
        }

        response.EnsureSuccessStatusCode();

        var body = await response.Content.ReadFromJsonAsync<VaultKvV2Response>(cancellationToken: cancellationToken);
        return body?.Data?.Data?.TryGetValue("value", out var val) == true ? val : null;
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

            var value = await GetAsync(botId, canonicalKey, cancellationToken);

            if (value is not null)
            {
                secrets[canonicalKey] = value;
            }
            else if (descriptor.Required)
            {
                throw new SecretNotFoundException(botId, canonicalKey);
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
    {
        // Force re-auth on refresh to ensure token is fresh
        _tokenExpiry = DateTimeOffset.MinValue;
        return GetBundleAsync(expiredBundle.BotId, descriptors, ttl, cancellationToken);
    }

    /// <summary>
    /// Translates a canonical key name to a Vault KV v2 path.
    /// Canonical: LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
    /// Vault:     legal-bot/westlaw/WESTLAW_API_KEY
    /// </summary>
    internal static string ToVaultPath(string canonicalKey)
    {
        // Split on double underscore: [BOT_NAME, APP_NAME, KEY_NAME]
        var parts = canonicalKey.Split("__", 3);
        if (parts.Length != 3)
            return canonicalKey.ToLowerInvariant().Replace("__", "/");

        var botSegment = parts[0].ToLowerInvariant().Replace("_", "-");
        var appSegment = parts[1].ToLowerInvariant().Replace("_", "-");
        var keySegment = parts[2]; // preserve original casing for key

        return $"{botSegment}/{appSegment}/{keySegment}";
    }

    private async Task EnsureAuthenticatedAsync(CancellationToken cancellationToken)
    {
        if (_vaultToken is not null && DateTimeOffset.UtcNow < _tokenExpiry)
            return;

        // Phase 1: AppRole authentication
        // Phase 3b hook: replace with SPIFFE SVID JWT auth method
        var loginPayload = new { role_id = _options.RoleId, secret_id = _options.SecretId };
        using var response = await _http.PostAsJsonAsync("/v1/auth/approle/login", loginPayload, cancellationToken);
        response.EnsureSuccessStatusCode();

        var authResponse = await response.Content.ReadFromJsonAsync<VaultAuthResponse>(cancellationToken: cancellationToken);
        _vaultToken = authResponse?.Auth?.ClientToken
            ?? throw new InvalidOperationException("Vault AppRole login did not return a client token.");

        var ttlSeconds = authResponse.Auth.LeaseDuration > 0 ? authResponse.Auth.LeaseDuration : 3600;
        // Expire slightly before actual TTL to avoid race conditions
        _tokenExpiry = DateTimeOffset.UtcNow.AddSeconds(ttlSeconds - 30);

        _logger.LogDebug("Vault AppRole authenticated; token expires ~{Expiry}", _tokenExpiry);
    }

    // Minimal Vault KV v2 response models — only fields needed for secret resolution
    private sealed record VaultKvV2Response(VaultKvV2Data? Data);
    private sealed record VaultKvV2Data(Dictionary<string, string>? Data);
    private sealed record VaultAuthResponse(VaultAuthToken? Auth);
    private sealed record VaultAuthToken(string ClientToken, int LeaseDuration);
}

/// <summary>Configuration options for <see cref="HashiCorpVaultProvider"/>.</summary>
public sealed class HashiCorpVaultOptions
{
    /// <summary>Base URL of the Vault server (e.g. "http://localhost:8200").</summary>
    public required string VaultAddress { get; init; }

    /// <summary>AppRole Role ID for this agent type. Phase 3b: replaced by SPIFFE SVID.</summary>
    public required string RoleId { get; init; }

    /// <summary>AppRole Secret ID (short-lived). Generated at agent spawn time, never stored long-term.</summary>
    public required string SecretId { get; init; }

    /// <summary>KV v2 mount path (default: "secret").</summary>
    public string? MountPath { get; init; }
}
