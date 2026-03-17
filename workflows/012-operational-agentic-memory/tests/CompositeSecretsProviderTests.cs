using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;
using PPA.Secrets;

namespace PPA.Secrets.Tests;

/// <summary>
/// Unit tests for <see cref="CompositeSecretsProvider"/>.
/// Covers fallback behavior, TTL expiry, and blocked secret enforcement.
/// Uses simple hand-rolled fakes — no mocking framework required.
/// </summary>
public sealed class CompositeSecretsProviderTests
{
    private static CompositeSecretsProvider Build(ISecretsProvider primary, ISecretsProvider fallback)
        => new(primary, fallback, NullLogger<CompositeSecretsProvider>.Instance);

    // -----------------------------------------------------------------------
    // GetAsync — primary succeeds
    // -----------------------------------------------------------------------

    [Fact]
    public async Task GetAsync_PrimaryReturnsValue_ReturnsPrimaryValue()
    {
        var primary = new StubProvider(results: new() { ["BOT__APP__KEY"] = "primary-value" });
        var fallback = new StubProvider(results: new() { ["BOT__APP__KEY"] = "fallback-value" });
        var composite = Build(primary, fallback);

        var result = await composite.GetAsync("bot", "BOT__APP__KEY");

        Assert.Equal("primary-value", result);
        Assert.Equal(1, primary.GetCallCount);
        Assert.Equal(0, fallback.GetCallCount);
    }

    // -----------------------------------------------------------------------
    // GetAsync — primary returns null, fallback used
    // -----------------------------------------------------------------------

    [Fact]
    public async Task GetAsync_PrimaryReturnsNull_FallbackIsTried()
    {
        var primary = new StubProvider(); // all nulls
        var fallback = new StubProvider(results: new() { ["BOT__APP__KEY"] = "fallback-value" });
        var composite = Build(primary, fallback);

        var result = await composite.GetAsync("bot", "BOT__APP__KEY");

        Assert.Equal("fallback-value", result);
        Assert.Equal(1, primary.GetCallCount);
        Assert.Equal(1, fallback.GetCallCount);
    }

    // -----------------------------------------------------------------------
    // GetAsync — primary throws, fallback used
    // -----------------------------------------------------------------------

    [Fact]
    public async Task GetAsync_PrimaryThrows_FallbackIsTried()
    {
        var primary = new StubProvider(shouldThrow: true);
        var fallback = new StubProvider(results: new() { ["BOT__APP__KEY"] = "fallback-value" });
        var composite = Build(primary, fallback);

        var result = await composite.GetAsync("bot", "BOT__APP__KEY");

        Assert.Equal("fallback-value", result);
        Assert.Equal(1, fallback.GetCallCount);
    }

    // -----------------------------------------------------------------------
    // GetAsync — blocked secret does NOT fall back
    // -----------------------------------------------------------------------

    [Fact]
    public async Task GetAsync_PrimaryThrowsSecretBlocked_NofallbackAttempted()
    {
        var primary = new StubProvider(shouldThrowBlocked: true);
        var fallback = new StubProvider(results: new() { ["BOT__APP__KEY"] = "fallback-value" });
        var composite = Build(primary, fallback);

        await Assert.ThrowsAsync<SecretBlockedException>(
            () => composite.GetAsync("bot", "BOT__APP__KEY"));

        // Fallback must NOT be tried when the block is intentional policy
        Assert.Equal(0, fallback.GetCallCount);
    }

    // -----------------------------------------------------------------------
    // GetAsync — both primary and fallback return null
    // -----------------------------------------------------------------------

    [Fact]
    public async Task GetAsync_BothVaultsReturnNull_ReturnsNull()
    {
        var primary = new StubProvider();
        var fallback = new StubProvider();
        var composite = Build(primary, fallback);

        var result = await composite.GetAsync("bot", "BOT__APP__KEY");

        Assert.Null(result);
    }

    // -----------------------------------------------------------------------
    // GetBundleAsync — primary succeeds
    // -----------------------------------------------------------------------

    [Fact]
    public async Task GetBundleAsync_PrimarySucceeds_ReturnsPrimaryBundle()
    {
        var descriptors = MakeDescriptors("app", "SOME_KEY");
        var expectedBundle = MakeBundle("bot");

        var primary = new StubProvider(bundle: expectedBundle);
        var fallback = new StubProvider();
        var composite = Build(primary, fallback);

        var result = await composite.GetBundleAsync("bot", descriptors, TimeSpan.FromMinutes(30));

        Assert.Equal(expectedBundle, result);
        Assert.Equal(0, fallback.BundleCallCount);
    }

    // -----------------------------------------------------------------------
    // GetBundleAsync — primary throws, fallback used
    // -----------------------------------------------------------------------

    [Fact]
    public async Task GetBundleAsync_PrimaryThrows_FallbackBundleReturned()
    {
        var descriptors = MakeDescriptors("app", "SOME_KEY");
        var fallbackBundle = MakeBundle("bot");

        var primary = new StubProvider(shouldThrow: true);
        var fallback = new StubProvider(bundle: fallbackBundle);
        var composite = Build(primary, fallback);

        var result = await composite.GetBundleAsync("bot", descriptors, TimeSpan.FromMinutes(30));

        Assert.Equal(fallbackBundle, result);
        Assert.Equal(1, fallback.BundleCallCount);
    }

    // -----------------------------------------------------------------------
    // GetBundleAsync — blocked secret does NOT fall back
    // -----------------------------------------------------------------------

    [Fact]
    public async Task GetBundleAsync_PrimaryThrowsSecretBlocked_NofallbackAttempted()
    {
        var descriptors = MakeDescriptors("app", "SOME_KEY");
        var fallbackBundle = MakeBundle("bot");

        var primary = new StubProvider(shouldThrowBlocked: true);
        var fallback = new StubProvider(bundle: fallbackBundle);
        var composite = Build(primary, fallback);

        await Assert.ThrowsAsync<SecretBlockedException>(
            () => composite.GetBundleAsync("bot", descriptors, TimeSpan.FromMinutes(30)));

        Assert.Equal(0, fallback.BundleCallCount);
    }

    // -----------------------------------------------------------------------
    // SecretBundle.IsValid — TTL expiry
    // -----------------------------------------------------------------------

    [Fact]
    public void SecretBundle_IsValid_ReturnsTrueBeforeExpiry()
    {
        var bundle = new SecretBundle(
            "bot",
            new Dictionary<string, string>(),
            DateTimeOffset.UtcNow,
            DateTimeOffset.UtcNow.AddMinutes(30));

        Assert.True(bundle.IsValid);
    }

    [Fact]
    public void SecretBundle_IsValid_ReturnsFalseAfterExpiry()
    {
        var bundle = new SecretBundle(
            "bot",
            new Dictionary<string, string>(),
            DateTimeOffset.UtcNow.AddMinutes(-60),
            DateTimeOffset.UtcNow.AddMinutes(-1)); // expired 1 minute ago

        Assert.False(bundle.IsValid);
    }

    [Fact]
    public void SecretBundle_IsValid_ReturnsFalseAtExactExpiry()
    {
        // One millisecond in the past
        var bundle = new SecretBundle(
            "bot",
            new Dictionary<string, string>(),
            DateTimeOffset.UtcNow.AddMinutes(-30),
            DateTimeOffset.UtcNow.AddMilliseconds(-1));

        Assert.False(bundle.IsValid);
    }

    // -----------------------------------------------------------------------
    // RefreshAsync — delegates to GetBundleAsync (state cleared)
    // -----------------------------------------------------------------------

    [Fact]
    public async Task RefreshAsync_CallsGetBundleWithSameBotId()
    {
        var descriptors = MakeDescriptors("app", "KEY");
        var newBundle = MakeBundle("bot");
        var primary = new StubProvider(bundle: newBundle);
        var composite = Build(primary, new StubProvider());

        var expiredBundle = new SecretBundle(
            "bot",
            new Dictionary<string, string>(),
            DateTimeOffset.UtcNow.AddMinutes(-60),
            DateTimeOffset.UtcNow.AddMinutes(-1));

        var result = await composite.RefreshAsync(expiredBundle, descriptors, TimeSpan.FromMinutes(30));

        Assert.Equal("bot", result.BotId);
        Assert.Equal(1, primary.BundleCallCount);
    }

    // -----------------------------------------------------------------------
    // Helpers
    // -----------------------------------------------------------------------

    private static IReadOnlyList<SecretDescriptor> MakeDescriptors(string appName, string key)
        => new[]
        {
            new SecretDescriptor(appName, key, Required: true,
                Scopes: Array.Empty<string>(), Blocked: Array.Empty<string>())
        };

    private static SecretBundle MakeBundle(string botId)
        => new(botId, new Dictionary<string, string>(),
            DateTimeOffset.UtcNow, DateTimeOffset.UtcNow.AddMinutes(30));

    // -----------------------------------------------------------------------
    // Stub provider — hand-rolled fake
    // -----------------------------------------------------------------------

    private sealed class StubProvider : ISecretsProvider
    {
        private readonly Dictionary<string, string> _results;
        private readonly bool _shouldThrow;
        private readonly bool _shouldThrowBlocked;
        private readonly SecretBundle? _bundle;

        public int GetCallCount { get; private set; }
        public int BundleCallCount { get; private set; }

        public StubProvider(
            Dictionary<string, string>? results = null,
            bool shouldThrow = false,
            bool shouldThrowBlocked = false,
            SecretBundle? bundle = null)
        {
            _results = results ?? new();
            _shouldThrow = shouldThrow;
            _shouldThrowBlocked = shouldThrowBlocked;
            _bundle = bundle;
        }

        public Task<string?> GetAsync(string botId, string canonicalKey, CancellationToken ct = default)
        {
            GetCallCount++;
            if (_shouldThrowBlocked) throw new SecretBlockedException(botId, canonicalKey);
            if (_shouldThrow) throw new InvalidOperationException("Simulated vault failure");
            _results.TryGetValue(canonicalKey, out var val);
            return Task.FromResult<string?>(val);
        }

        public Task<SecretBundle> GetBundleAsync(
            string botId, IReadOnlyList<SecretDescriptor> descriptors, TimeSpan ttl, CancellationToken ct = default)
        {
            BundleCallCount++;
            if (_shouldThrowBlocked) throw new SecretBlockedException(botId, "BLOCKED_KEY");
            if (_shouldThrow) throw new InvalidOperationException("Simulated vault failure");
            return Task.FromResult(_bundle ?? MakeBundle(botId));
        }

        public Task<SecretBundle> RefreshAsync(
            SecretBundle expiredBundle, IReadOnlyList<SecretDescriptor> descriptors, TimeSpan ttl, CancellationToken ct = default)
            => GetBundleAsync(expiredBundle.BotId, descriptors, ttl, ct);

        private static SecretBundle MakeBundle(string botId)
            => new(botId, new Dictionary<string, string>(),
                DateTimeOffset.UtcNow, DateTimeOffset.UtcNow.AddMinutes(30));
    }
}
