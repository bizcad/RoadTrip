using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace PPA.Secrets;

/// <summary>
/// Descriptor for a single secret within a bot's manifest.
/// Carries metadata about the secret's purpose, requirements, and scope constraints —
/// never the secret value itself.
/// </summary>
/// <param name="AppName">The application or service that owns this credential (e.g. "westlaw", "anthropic").</param>
/// <param name="CanonicalKey">The canonical key name in UPPER_SNAKE_CASE (e.g. "WESTLAW_API_KEY").</param>
/// <param name="Required">Whether the bot must fail startup if this secret cannot be resolved.</param>
/// <param name="Scopes">Fine-grained capabilities this secret unlocks (e.g. ["case-law-search"]).</param>
/// <param name="Blocked">Canonical key names that this bot is explicitly forbidden from requesting, regardless of delegation.</param>
public record SecretDescriptor(
    string AppName,
    string CanonicalKey,
    bool Required,
    IReadOnlyList<string> Scopes,
    IReadOnlyList<string> Blocked);

/// <summary>
/// A resolved, time-bound bundle of secrets scoped to a single bot identity.
/// Corresponds to the least-privilege bundle model in unified-auth-spec-v0.2 Section 3.3.
/// </summary>
/// <param name="BotId">The identity of the bot that owns this bundle (e.g. "legal-bot").</param>
/// <param name="Secrets">
/// Resolved secret values keyed by canonical name ({BOT_NAME}__{APP_NAME}__{KEY_NAME}).
/// Values are in-memory only and must not be persisted or logged.
/// </param>
/// <param name="IssuedAt">When this bundle was resolved from the vault.</param>
/// <param name="ExpiresAt">When this bundle must be considered stale and refreshed.</param>
public record SecretBundle(
    string BotId,
    IReadOnlyDictionary<string, string> Secrets,
    DateTimeOffset IssuedAt,
    DateTimeOffset ExpiresAt)
{
    /// <summary>Returns true if the bundle is still within its validity window.</summary>
    public bool IsValid => DateTimeOffset.UtcNow < ExpiresAt;
}

/// <summary>
/// Core abstraction for resolving secrets from an underlying vault or secret store.
/// Implementations must never log secret values; only canonical key names may appear in logs.
/// </summary>
/// <remarks>
/// This interface is the PEP-adjacent boundary described in unified-auth-spec-v0.2 Section 5:
/// it translates the abstract "agent needs WESTLAW_API_KEY" into a vault-specific retrieval,
/// enforcing the blocked list and delegation scope before any vault call is made.
/// </remarks>
public interface ISecretsProvider
{
    /// <summary>
    /// Retrieves a single secret value by its canonical key name for a given bot.
    /// </summary>
    /// <param name="botId">The bot identity (e.g. "legal-bot").</param>
    /// <param name="canonicalKey">
    /// Canonical name in the form {BOT_NAME}__{APP_NAME}__{KEY_NAME}
    /// (e.g. "LEGAL_BOT__WESTLAW__WESTLAW_API_KEY").
    /// </param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The secret value, or null if not found and the key is not required.</returns>
    /// <exception cref="SecretBlockedException">Thrown when the key appears in the bot's blocked list.</exception>
    /// <exception cref="SecretNotFoundException">Thrown when the key is required but could not be resolved.</exception>
    Task<string?> GetAsync(
        string botId,
        string canonicalKey,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Resolves a full secret bundle for the given bot, using its manifest descriptors.
    /// All required secrets must resolve; optional secrets that fail are omitted from the bundle.
    /// </summary>
    /// <param name="botId">The bot identity.</param>
    /// <param name="descriptors">
    /// The bot's declared secret needs, typically decoded from its <c>secrets-manifest.enc</c>.
    /// </param>
    /// <param name="ttl">How long the returned bundle should be considered valid.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task<SecretBundle> GetBundleAsync(
        string botId,
        IReadOnlyList<SecretDescriptor> descriptors,
        TimeSpan ttl,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Forces a refresh of any cached values for the given bot, then returns an updated bundle.
    /// Call this when a bundle's <see cref="SecretBundle.IsValid"/> returns false.
    /// </summary>
    /// <param name="expiredBundle">The bundle to refresh.</param>
    /// <param name="descriptors">The bot's current manifest descriptors.</param>
    /// <param name="ttl">TTL for the new bundle.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task<SecretBundle> RefreshAsync(
        SecretBundle expiredBundle,
        IReadOnlyList<SecretDescriptor> descriptors,
        TimeSpan ttl,
        CancellationToken cancellationToken = default);
}

/// <summary>Thrown when a bot attempts to retrieve a secret that appears on its blocked list.</summary>
public sealed class SecretBlockedException(string botId, string canonicalKey)
    : InvalidOperationException(
        $"Bot '{botId}' is not permitted to access secret '{canonicalKey}'. " +
        "Review the blocked list in the bot's secrets manifest.");

/// <summary>Thrown when a required secret cannot be resolved from any provider.</summary>
public sealed class SecretNotFoundException(string botId, string canonicalKey)
    : KeyNotFoundException(
        $"Required secret '{canonicalKey}' for bot '{botId}' could not be resolved from any vault.");
