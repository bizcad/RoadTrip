using System;
using System.Text.RegularExpressions;

namespace PPA.Secrets;

/// <summary>
/// Translates secret names between the canonical form and the five target formats
/// used across the PPA secrets plane.
/// </summary>
/// <remarks>
/// Canonical form: {BOT_NAME}__{APP_NAME}__{KEY_NAME}
/// All tokens are UPPER_SNAKE_CASE in canonical form. The translator normalizes
/// input before conversion, so "legal-bot", "legal_bot", and "LEGAL_BOT" all
/// produce the same canonical output.
///
/// This is a pure-function static class with no dependencies — fully unit testable
/// without mocks or infrastructure.
/// </remarks>
public static class SecretNameTranslator
{
    // Pattern for a valid name segment: letters, digits, hyphens, underscores.
    private static readonly Regex ValidSegment = new(@"^[a-zA-Z0-9][a-zA-Z0-9_\-]*$", RegexOptions.Compiled);

    /// <summary>
    /// Builds the canonical key name from its three components.
    /// Canonical: LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
    /// </summary>
    /// <param name="botName">Bot identifier (e.g. "legal-bot" or "LEGAL_BOT").</param>
    /// <param name="appName">Application/service name (e.g. "westlaw" or "WESTLAW").</param>
    /// <param name="keyName">Key identifier in UPPER_SNAKE_CASE (e.g. "WESTLAW_API_KEY").</param>
    public static string ToCanonical(string botName, string appName, string keyName)
    {
        Validate(nameof(botName), botName);
        Validate(nameof(appName), appName);
        Validate(nameof(keyName), keyName);

        return $"{Normalize(botName)}__{Normalize(appName)}__{Normalize(keyName)}";
    }

    /// <summary>
    /// Translates a canonical key name to Azure Key Vault format.
    /// AKV does not allow underscores or forward slashes in secret names.
    /// Canonical: LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
    /// AKV:       legal-bot--westlaw--westlaw-api-key
    /// </summary>
    public static string ToAzureKeyVault(string canonicalKey)
        => canonicalKey
            .Replace("__", "--")   // double-underscore segment separator → double-dash
            .Replace("_", "-")     // single-underscore within a segment → single-dash
            .ToLowerInvariant();

    /// <summary>
    /// Translates a canonical key name to HashiCorp Vault OSS path (KV v2).
    /// Canonical: LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
    /// Vault:     legal-bot/westlaw/WESTLAW_API_KEY
    /// </summary>
    public static string ToHashiCorpVault(string canonicalKey)
    {
        var parts = canonicalKey.Split("__", 3);
        if (parts.Length != 3)
            throw new ArgumentException($"Canonical key must have exactly 3 segments separated by '__': {canonicalKey}");

        var botSegment = parts[0].ToLowerInvariant().Replace("_", "-");
        var appSegment = parts[1].ToLowerInvariant().Replace("_", "-");
        // Preserve original casing for key name — Vault is case-sensitive
        var keySegment = parts[2];

        return $"{botSegment}/{appSegment}/{keySegment}";
    }

    /// <summary>
    /// Translates a canonical key name to environment variable format.
    /// Canonical and env var formats are identical (UPPER_SNAKE_CASE with __ separator).
    /// Canonical: LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
    /// Env var:   LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
    /// </summary>
    /// <remarks>
    /// The double-underscore convention is the .NET IConfiguration hierarchy separator,
    /// enabling direct use with <c>IConfiguration["LEGAL_BOT:WESTLAW:WESTLAW_API_KEY"]</c>
    /// when the provider uses <c>__</c> as the section delimiter.
    /// </remarks>
    public static string ToEnvVar(string canonicalKey)
        => canonicalKey.ToUpperInvariant();

    /// <summary>
    /// Translates a canonical key name to GitHub Actions secret format.
    /// GitHub Secrets names must be UPPER_SNAKE_CASE, no dashes allowed.
    /// Canonical: LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
    /// GitHub:    LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
    /// </summary>
    public static string ToGitHubSecret(string canonicalKey)
        => canonicalKey.ToUpperInvariant().Replace("-", "_");

    /// <summary>
    /// Translates a canonical key name to Vercel environment variable format.
    /// Vercel env vars follow the same UPPER_SNAKE_CASE convention as standard env vars.
    /// Canonical: LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
    /// Vercel:    LEGAL_BOT__WESTLAW__WESTLAW_API_KEY
    /// </summary>
    public static string ToVercelEnv(string canonicalKey)
        => canonicalKey.ToUpperInvariant();

    /// <summary>
    /// Parses a canonical key name into its three components.
    /// Returns (botName, appName, keyName) or throws if the key is malformed.
    /// </summary>
    public static (string BotName, string AppName, string KeyName) Parse(string canonicalKey)
    {
        var parts = canonicalKey.Split("__", 3);
        if (parts.Length != 3)
            throw new ArgumentException(
                $"Canonical key must have exactly 3 '__'-separated segments. Got: '{canonicalKey}'");
        return (parts[0], parts[1], parts[2]);
    }

    // Normalizes a name component: lowercase hyphenated form → UPPER_SNAKE_CASE
    private static string Normalize(string segment)
        => segment.Trim().ToUpperInvariant().Replace("-", "_");

    private static void Validate(string paramName, string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new ArgumentException($"Segment '{paramName}' must not be null or whitespace.");

        // Validate after normalizing to UPPER_SNAKE_CASE
        var normalized = value.ToUpperInvariant().Replace("-", "_");
        if (!ValidSegment.IsMatch(normalized))
            throw new ArgumentException(
                $"Segment '{paramName}' contains invalid characters after normalization: '{normalized}'. " +
                "Only letters, digits, underscores, and hyphens are permitted.");
    }
}
