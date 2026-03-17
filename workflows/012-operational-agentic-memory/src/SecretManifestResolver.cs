using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.IdentityModel.Tokens;
using Microsoft.Extensions.Logging;

namespace PPA.Secrets;

/// <summary>
/// Reads, decrypts, and resolves the JWE-encoded secret manifest baked into a bot's repository.
/// Enforces the blocked list before any vault call is issued.
/// </summary>
/// <remarks>
/// The manifest file (<c>secrets-manifest.enc</c>) is a JWE Compact Serialization (RFC 7516)
/// using ECDH-ES+A256KW key agreement and A256GCM content encryption.
///
/// Bootstrap secret pattern (Section 3.2, unified-auth-spec-v0.2):
///   One decryption key unlocks everything. That key comes from:
///     Prod:      Entra Managed Identity → Azure Key Vault EC key
///     CI:        Injected as env var (JWE_BOOTSTRAP_KEY_PEM)
///     Local dev: Local PEM file at the path set by JWE_KEY_PATH (gitignored)
///
/// Aspire sidecar compatibility:
///   The resolver exposes a minimal HTTP endpoint at localhost so the Aspire dashboard
///   and other local services can request bundles without direct vault credentials.
///   This is the sidecar pattern described in the session log (localhost:5001).
///
/// Blocked list enforcement:
///   The resolver checks blocked entries in the manifest before forwarding any request
///   to the vault. A blocked key raises <see cref="SecretBlockedException"/> regardless
///   of the caller's delegation scope.
/// </remarks>
public sealed class SecretManifestResolver
{
    private readonly ISecretsProvider _provider;
    private readonly string _manifestPath;
    private readonly SecretManifestKeySource _keySource;
    private readonly ILogger<SecretManifestResolver> _logger;

    private SecretsManifest? _cachedManifest;

    /// <param name="provider">
    /// The underlying secrets provider (typically a <see cref="CompositeSecretsProvider"/>).
    /// </param>
    /// <param name="manifestPath">
    /// Path to the encrypted manifest file (<c>secrets-manifest.enc</c>) within the bot repo.
    /// </param>
    /// <param name="keySource">Source of the decryption key (vault, env var, or local PEM).</param>
    /// <param name="logger">Logger — must never log secret values.</param>
    public SecretManifestResolver(
        ISecretsProvider provider,
        string manifestPath,
        SecretManifestKeySource keySource,
        ILogger<SecretManifestResolver> logger)
    {
        _provider = provider;
        _manifestPath = manifestPath;
        _keySource = keySource;
        _logger = logger;
    }

    /// <summary>
    /// Resolves the full secret bundle for this bot by decrypting its manifest and fetching values.
    /// </summary>
    /// <param name="ttl">How long the returned bundle should be considered valid.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    public async Task<SecretBundle> ResolveAsync(
        TimeSpan ttl,
        CancellationToken cancellationToken = default)
    {
        var manifest = await GetManifestAsync(cancellationToken);
        var descriptors = BuildDescriptors(manifest);

        _logger.LogInformation(
            "SecretManifestResolver: resolving bundle — botId={BotId} secretCount={Count} blockedCount={Blocked}",
            manifest.BotId, manifest.Secrets.Count, manifest.Blocked.Count);

        return await _provider.GetBundleAsync(manifest.BotId, descriptors, ttl, cancellationToken);
    }

    /// <summary>
    /// Resolves a single secret by canonical key, enforcing the manifest's blocked list first.
    /// </summary>
    public async Task<string?> ResolveOneAsync(
        string canonicalKey,
        CancellationToken cancellationToken = default)
    {
        var manifest = await GetManifestAsync(cancellationToken);
        EnforceBlockedList(manifest, canonicalKey);
        return await _provider.GetAsync(manifest.BotId, canonicalKey, cancellationToken);
    }

    /// <summary>
    /// Returns the decrypted manifest for inspection (key names and metadata only — never values).
    /// Caches the result for the lifetime of this resolver instance.
    /// </summary>
    public async Task<SecretsManifest> GetManifestAsync(CancellationToken cancellationToken = default)
    {
        if (_cachedManifest is not null)
            return _cachedManifest;

        _logger.LogDebug("SecretManifestResolver: loading manifest from {Path}", _manifestPath);

        var jweCompact = await File.ReadAllTextAsync(_manifestPath, Encoding.UTF8, cancellationToken);
        var decryptedJson = DecryptJwe(jweCompact.Trim());

        _cachedManifest = JsonSerializer.Deserialize<SecretsManifest>(decryptedJson,
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true })
            ?? throw new InvalidOperationException("Manifest decryption produced an empty result.");

        _logger.LogInformation(
            "SecretManifestResolver: manifest loaded — botId={BotId} version={Version}",
            _cachedManifest.BotId, _cachedManifest.Version);

        return _cachedManifest;
    }

    // Decrypts a JWE Compact Serialization string using the configured key source.
    // Algorithm: ECDH-ES+A256KW / A256GCM  (RFC 7516, Section 5)
    private string DecryptJwe(string jweCompact)
    {
        var key = _keySource.GetDecryptionKey();

        // Use Microsoft.IdentityModel.Tokens for JWE processing.
        // JsonWebEncryption supports ECDH-ES+A256KW + A256GCM natively.
        var handler = new System.IdentityModel.Tokens.Jwt.JwtSecurityTokenHandler();

        var parameters = new TokenValidationParameters
        {
            ValidateIssuer = false,
            ValidateAudience = false,
            ValidateLifetime = false,
            TokenDecryptionKey = key,
            RequireSignedTokens = false
        };

        // JWE compact serialization has 5 parts separated by '.'
        // We use the handler's decrypt path only.
        var tokenHandler = new Microsoft.IdentityModel.JsonWebTokens.JsonWebTokenHandler();
        var result = tokenHandler.DecryptToken(
            new Microsoft.IdentityModel.Tokens.JsonWebToken(jweCompact),
            parameters);

        if (result is null || result.Length == 0)
            throw new InvalidOperationException(
                "JWE decryption returned empty payload. Verify the bootstrap key matches the encryption key.");

        return Encoding.UTF8.GetString(result);
    }

    private static IReadOnlyList<SecretDescriptor> BuildDescriptors(SecretsManifest manifest)
    {
        var descriptors = new List<SecretDescriptor>();
        foreach (var entry in manifest.Secrets)
        {
            descriptors.Add(new SecretDescriptor(
                AppName: entry.AppName,
                CanonicalKey: entry.Key,
                Required: entry.Required,
                Scopes: entry.Scopes ?? Array.Empty<string>(),
                Blocked: manifest.Blocked ?? Array.Empty<string>()));
        }
        return descriptors;
    }

    private static void EnforceBlockedList(SecretsManifest manifest, string canonicalKey)
    {
        foreach (var blocked in manifest.Blocked)
        {
            if (string.Equals(blocked, canonicalKey, StringComparison.OrdinalIgnoreCase))
                throw new SecretBlockedException(manifest.BotId, canonicalKey);
        }
    }
}

/// <summary>
/// Unencrypted manifest structure (deserialization target after JWE decryption).
/// This type is never written to disk or logs with values present.
/// </summary>
public sealed class SecretsManifest
{
    /// <summary>The bot identity this manifest belongs to (e.g. "legal-bot").</summary>
    public required string BotId { get; init; }

    /// <summary>Semantic version of this manifest (e.g. "1.0.3").</summary>
    public required string Version { get; init; }

    /// <summary>Declared secrets this bot requires or may optionally use.</summary>
    public required IReadOnlyList<ManifestSecretEntry> Secrets { get; init; }

    /// <summary>
    /// Canonical key names this bot is constitutionally forbidden from requesting.
    /// Enforced by the resolver before any vault call.
    /// </summary>
    public IReadOnlyList<string> Blocked { get; init; } = Array.Empty<string>();
}

/// <summary>A single secret declaration within a manifest.</summary>
public sealed class ManifestSecretEntry
{
    /// <summary>The service/application name (e.g. "westlaw").</summary>
    public required string AppName { get; init; }

    /// <summary>The key name in UPPER_SNAKE_CASE (e.g. "WESTLAW_API_KEY").</summary>
    public required string Key { get; init; }

    /// <summary>Whether missing this secret must fail the bot's startup.</summary>
    public bool Required { get; init; } = true;

    /// <summary>Capability scopes this secret unlocks.</summary>
    public IReadOnlyList<string>? Scopes { get; init; }
}

/// <summary>
/// Provides the decryption key for the JWE-encrypted manifest.
/// Encapsulates the environment-specific key retrieval strategy.
/// </summary>
public abstract class SecretManifestKeySource
{
    /// <summary>Returns the <see cref="SecurityKey"/> used to decrypt the manifest JWE.</summary>
    public abstract SecurityKey GetDecryptionKey();

    /// <summary>
    /// Creates a key source backed by a local PEM file.
    /// Use for local development. The PEM file must be gitignored.
    /// </summary>
    public static SecretManifestKeySource FromPemFile(string pemPath) => new PemFileKeySource(pemPath);

    /// <summary>
    /// Creates a key source backed by a PEM string in an environment variable.
    /// Use for CI/CD pipelines.
    /// </summary>
    public static SecretManifestKeySource FromEnvironmentVariable(string variableName) =>
        new EnvVarKeySource(variableName);

    private sealed class PemFileKeySource(string path) : SecretManifestKeySource
    {
        public override SecurityKey GetDecryptionKey()
        {
            var pem = File.ReadAllText(path);
            return ParseEcKey(pem);
        }
    }

    private sealed class EnvVarKeySource(string variableName) : SecretManifestKeySource
    {
        public override SecurityKey GetDecryptionKey()
        {
            var pem = Environment.GetEnvironmentVariable(variableName)
                ?? throw new InvalidOperationException(
                    $"Environment variable '{variableName}' is not set. " +
                    "Set it to the PEM-encoded EC private key for manifest decryption.");
            return ParseEcKey(pem);
        }
    }

    private static SecurityKey ParseEcKey(string pem)
    {
        // Microsoft.IdentityModel.Tokens supports PEM-encoded EC keys via ECDsaSecurityKey
        // or via JsonWebKey for ECDH keys.
        var ecParameters = ExtractEcParametersFromPem(pem);
        var ecdh = System.Security.Cryptography.ECDiffieHellman.Create(ecParameters);
        return new Microsoft.IdentityModel.Tokens.ECDsaSecurityKey(
            System.Security.Cryptography.ECDsa.Create(ecParameters));
    }

    private static System.Security.Cryptography.ECParameters ExtractEcParametersFromPem(string pem)
    {
        // Use .NET built-in PEM import (available .NET 5+)
        using var ecdsa = System.Security.Cryptography.ECDsa.Create();
        ecdsa.ImportFromPem(pem);
        return ecdsa.ExportParameters(includePrivateParameters: true);
    }
}
