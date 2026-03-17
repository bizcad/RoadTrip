using System;
using Xunit;
using PPA.Secrets;

namespace PPA.Secrets.Tests;

/// <summary>
/// Unit tests for <see cref="SecretNameTranslator"/>.
/// All five translation formats, normalization, and edge cases.
/// No mocks required — SecretNameTranslator is a pure static class.
/// </summary>
public sealed class SecretNameTranslatorTests
{
    // -----------------------------------------------------------------------
    // ToCanonical
    // -----------------------------------------------------------------------

    [Theory]
    [InlineData("legal-bot", "westlaw", "WESTLAW_API_KEY", "LEGAL_BOT__WESTLAW__WESTLAW_API_KEY")]
    [InlineData("LEGAL_BOT", "WESTLAW", "WESTLAW_API_KEY", "LEGAL_BOT__WESTLAW__WESTLAW_API_KEY")]
    [InlineData("legal_bot", "westlaw", "WESTLAW_API_KEY", "LEGAL_BOT__WESTLAW__WESTLAW_API_KEY")]
    [InlineData("marketing-bot", "twitter", "TWITTER_BEARER_TOKEN", "MARKETING_BOT__TWITTER__TWITTER_BEARER_TOKEN")]
    [InlineData("triage-agent", "anthropic", "ANTHROPIC_API_KEY", "TRIAGE_AGENT__ANTHROPIC__ANTHROPIC_API_KEY")]
    public void ToCanonical_StandardInputs_ReturnsUpperSnakeWithDoubleDash(
        string botName, string appName, string keyName, string expected)
    {
        var result = SecretNameTranslator.ToCanonical(botName, appName, keyName);
        Assert.Equal(expected, result);
    }

    [Fact]
    public void ToCanonical_MixedCaseHyphenInput_NormalizesToUpperSnake()
    {
        var result = SecretNameTranslator.ToCanonical("Legal-Bot", "West-Law", "api-key");
        Assert.Equal("LEGAL_BOT__WEST_LAW__API_KEY", result);
    }

    [Fact]
    public void ToCanonical_NullBotName_ThrowsArgumentException()
    {
        Assert.Throws<ArgumentException>(() =>
            SecretNameTranslator.ToCanonical(null!, "westlaw", "KEY"));
    }

    [Fact]
    public void ToCanonical_WhitespaceBotName_ThrowsArgumentException()
    {
        Assert.Throws<ArgumentException>(() =>
            SecretNameTranslator.ToCanonical("  ", "westlaw", "KEY"));
    }

    // -----------------------------------------------------------------------
    // ToAzureKeyVault
    // -----------------------------------------------------------------------

    [Theory]
    [InlineData("LEGAL_BOT__WESTLAW__WESTLAW_API_KEY", "legal-bot--westlaw--westlaw-api-key")]
    [InlineData("MARKETING_BOT__TWITTER__TWITTER_BEARER_TOKEN", "marketing-bot--twitter--twitter-bearer-token")]
    [InlineData("TRIAGE_AGENT__ANTHROPIC__ANTHROPIC_API_KEY", "triage-agent--anthropic--anthropic-api-key")]
    public void ToAzureKeyVault_CanonicalInput_ReturnsLowercaseDoubleDash(
        string canonical, string expected)
    {
        var result = SecretNameTranslator.ToAzureKeyVault(canonical);
        Assert.Equal(expected, result);
    }

    [Fact]
    public void ToAzureKeyVault_ResultContainsNeitherSlashNorUnderscore()
    {
        var result = SecretNameTranslator.ToAzureKeyVault("LEGAL_BOT__WESTLAW__WESTLAW_API_KEY");
        Assert.DoesNotContain("/", result);
        Assert.DoesNotContain("_", result);
    }

    // -----------------------------------------------------------------------
    // ToHashiCorpVault
    // -----------------------------------------------------------------------

    [Theory]
    [InlineData("LEGAL_BOT__WESTLAW__WESTLAW_API_KEY", "legal-bot/westlaw/WESTLAW_API_KEY")]
    [InlineData("MARKETING_BOT__TWITTER__TWITTER_BEARER_TOKEN", "marketing-bot/twitter/TWITTER_BEARER_TOKEN")]
    [InlineData("TRIAGE_AGENT__ANTHROPIC__ANTHROPIC_API_KEY", "triage-agent/anthropic/ANTHROPIC_API_KEY")]
    public void ToHashiCorpVault_CanonicalInput_ReturnsSlashSeparatedPath(
        string canonical, string expected)
    {
        var result = SecretNameTranslator.ToHashiCorpVault(canonical);
        Assert.Equal(expected, result);
    }

    [Fact]
    public void ToHashiCorpVault_KeyNamePreservesOriginalCasing()
    {
        // Vault is case-sensitive — key name must NOT be lowercased
        var result = SecretNameTranslator.ToHashiCorpVault("LEGAL_BOT__WESTLAW__WESTLAW_API_KEY");
        Assert.EndsWith("/WESTLAW_API_KEY", result);
    }

    [Fact]
    public void ToHashiCorpVault_TwoSegmentInput_ThrowsArgumentException()
    {
        Assert.Throws<ArgumentException>(() =>
            SecretNameTranslator.ToHashiCorpVault("LEGAL_BOT__WESTLAW_API_KEY"));
    }

    // -----------------------------------------------------------------------
    // ToEnvVar
    // -----------------------------------------------------------------------

    [Theory]
    [InlineData("LEGAL_BOT__WESTLAW__WESTLAW_API_KEY", "LEGAL_BOT__WESTLAW__WESTLAW_API_KEY")]
    [InlineData("legal_bot__westlaw__westlaw_api_key", "LEGAL_BOT__WESTLAW__WESTLAW_API_KEY")]
    public void ToEnvVar_ReturnsUpperSnakeUnchanged(string canonical, string expected)
    {
        Assert.Equal(expected, SecretNameTranslator.ToEnvVar(canonical));
    }

    // -----------------------------------------------------------------------
    // ToGitHubSecret
    // -----------------------------------------------------------------------

    [Theory]
    [InlineData("LEGAL_BOT__WESTLAW__WESTLAW_API_KEY", "LEGAL_BOT__WESTLAW__WESTLAW_API_KEY")]
    [InlineData("legal-bot__westlaw__key", "LEGAL_BOT__WESTLAW__KEY")]
    public void ToGitHubSecret_NoHyphensInResult(string canonical, string expected)
    {
        var result = SecretNameTranslator.ToGitHubSecret(canonical);
        Assert.Equal(expected, result);
        Assert.DoesNotContain("-", result);
    }

    // -----------------------------------------------------------------------
    // ToVercelEnv
    // -----------------------------------------------------------------------

    [Fact]
    public void ToVercelEnv_MatchesEnvVarFormat()
    {
        var canonical = "LEGAL_BOT__WESTLAW__WESTLAW_API_KEY";
        Assert.Equal(SecretNameTranslator.ToEnvVar(canonical),
                     SecretNameTranslator.ToVercelEnv(canonical));
    }

    // -----------------------------------------------------------------------
    // Parse
    // -----------------------------------------------------------------------

    [Fact]
    public void Parse_CanonicalKey_ReturnsTupleOfThreeSegments()
    {
        var (bot, app, key) = SecretNameTranslator.Parse("LEGAL_BOT__WESTLAW__WESTLAW_API_KEY");
        Assert.Equal("LEGAL_BOT", bot);
        Assert.Equal("WESTLAW", app);
        Assert.Equal("WESTLAW_API_KEY", key);
    }

    [Fact]
    public void Parse_TwoSegmentInput_ThrowsArgumentException()
    {
        Assert.Throws<ArgumentException>(() =>
            SecretNameTranslator.Parse("LEGAL_BOT__WESTLAW_API_KEY"));
    }

    // -----------------------------------------------------------------------
    // Roundtrip: canonical → AKV → verify no information loss possible
    // -----------------------------------------------------------------------

    [Theory]
    [InlineData("LEGAL_BOT__WESTLAW__WESTLAW_API_KEY")]
    [InlineData("MARKETING_BOT__TWITTER__TWITTER_BEARER_TOKEN")]
    [InlineData("TRIAGE_AGENT__ANTHROPIC__ANTHROPIC_API_KEY")]
    public void AllFormats_DeriveFromSameCanonical_NoInformationLoss(string canonical)
    {
        // All five formats must be deterministic given the same canonical input
        var akv1 = SecretNameTranslator.ToAzureKeyVault(canonical);
        var akv2 = SecretNameTranslator.ToAzureKeyVault(canonical);
        Assert.Equal(akv1, akv2);

        var vault1 = SecretNameTranslator.ToHashiCorpVault(canonical);
        var vault2 = SecretNameTranslator.ToHashiCorpVault(canonical);
        Assert.Equal(vault1, vault2);

        // Env, GitHub, Vercel all map to the same UPPER_SNAKE form
        var envVar = SecretNameTranslator.ToEnvVar(canonical);
        var github = SecretNameTranslator.ToGitHubSecret(canonical);
        var vercel = SecretNameTranslator.ToVercelEnv(canonical);
        Assert.Equal(envVar, github);
        Assert.Equal(envVar, vercel);
    }

    // -----------------------------------------------------------------------
    // AzureKeyVaultProvider.ToAkvName (internal, tested via provider)
    // -----------------------------------------------------------------------

    [Theory]
    [InlineData("LEGAL_BOT__WESTLAW__WESTLAW_API_KEY", "legal-bot--westlaw--westlaw-api-key")]
    public void AkvProviderToAkvName_MatchesTranslatorOutput(string canonical, string expected)
    {
        // Verify AzureKeyVaultProvider's internal translation is consistent with SecretNameTranslator
        var providerResult = AzureKeyVaultProvider.ToAkvName(canonical);
        var translatorResult = SecretNameTranslator.ToAzureKeyVault(canonical);
        Assert.Equal(expected, providerResult);
        Assert.Equal(expected, translatorResult);
    }

    // -----------------------------------------------------------------------
    // HashiCorpVaultProvider.ToVaultPath (internal, tested via provider)
    // -----------------------------------------------------------------------

    [Theory]
    [InlineData("LEGAL_BOT__WESTLAW__WESTLAW_API_KEY", "legal-bot/westlaw/WESTLAW_API_KEY")]
    public void VaultProviderToVaultPath_MatchesTranslatorOutput(string canonical, string expected)
    {
        var providerResult = HashiCorpVaultProvider.ToVaultPath(canonical);
        var translatorResult = SecretNameTranslator.ToHashiCorpVault(canonical);
        Assert.Equal(expected, providerResult);
        Assert.Equal(expected, translatorResult);
    }
}
