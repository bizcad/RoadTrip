using System;
using Aspire.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace PPA.Secrets;

/// <summary>
/// Extension methods for wiring the dual-vault secrets plane into an Aspire host.
/// Registers the correct <see cref="ISecretsProvider"/> composition per environment.
/// </summary>
/// <remarks>
/// Environment-specific provider ordering:
///
///   Development:
///     PRIMARY  — HashiCorp Vault OSS (localhost:8200, AppRole)
///     FALLBACK — .NET User Secrets (IConfiguration)
///
///   CI (GitHub Actions / Azure Pipelines):
///     PRIMARY  — Environment variables (injected by CI platform)
///     FALLBACK — Azure Key Vault (federated OIDC service principal)
///
///   Production:
///     PRIMARY  — Azure Key Vault (Entra Managed Identity)
///     FALLBACK — HashiCorp Vault OSS (AppRole, warm replica)
///
/// The consuming code always injects <see cref="ISecretsProvider"/> and never
/// knows which backing vault answered.
/// </remarks>
public static class SecretsExtensions
{
    /// <summary>
    /// Registers the dual-vault <see cref="ISecretsProvider"/> for the current environment.
    /// Call this from your <c>Program.cs</c> / <c>AppHost</c> service configuration.
    /// </summary>
    /// <param name="services">The service collection.</param>
    /// <param name="environment">The current host environment (used to select provider order).</param>
    /// <param name="options">Vault configuration options.</param>
    public static IServiceCollection AddPpaSecretsProvider(
        this IServiceCollection services,
        IHostEnvironment environment,
        PpaSecretsOptions options)
    {
        services.AddSingleton(options);

        if (environment.IsDevelopment())
        {
            RegisterDevelopmentProviders(services, options);
        }
        else if (IsCI())
        {
            RegisterCiProviders(services, options);
        }
        else
        {
            RegisterProductionProviders(services, options);
        }

        return services;
    }

    // Development: HashiCorp Vault OSS primary → User Secrets fallback
    private static void RegisterDevelopmentProviders(IServiceCollection services, PpaSecretsOptions options)
    {
        services.AddSingleton<ISecretsProvider>(sp =>
        {
            var logger = sp.GetRequiredService<ILogger<CompositeSecretsProvider>>();
            var vaultLogger = sp.GetRequiredService<ILogger<HashiCorpVaultProvider>>();
            var userSecretsLogger = sp.GetRequiredService<ILogger<EnvironmentVariableSecretsProvider>>();

            var primary = new HashiCorpVaultProvider(
                new HashiCorpVaultOptions
                {
                    VaultAddress = options.HashiCorpVaultAddress ?? "http://localhost:8200",
                    RoleId = options.DevRoleId ?? throw new InvalidOperationException(
                        "PpaSecretsOptions.DevRoleId must be set for Development environment."),
                    SecretId = options.DevSecretId ?? throw new InvalidOperationException(
                        "PpaSecretsOptions.DevSecretId must be set for Development environment.")
                },
                vaultLogger);

            // Fallback: environment variables / dotnet user-secrets (IConfiguration-backed)
            var fallback = new EnvironmentVariableSecretsProvider(userSecretsLogger);

            return new CompositeSecretsProvider(primary, fallback, logger);
        });
    }

    // CI: Environment variables primary → Azure Key Vault fallback
    private static void RegisterCiProviders(IServiceCollection services, PpaSecretsOptions options)
    {
        services.AddSingleton<ISecretsProvider>(sp =>
        {
            var logger = sp.GetRequiredService<ILogger<CompositeSecretsProvider>>();
            var envLogger = sp.GetRequiredService<ILogger<EnvironmentVariableSecretsProvider>>();
            var akvLogger = sp.GetRequiredService<ILogger<AzureKeyVaultProvider>>();

            var primary = new EnvironmentVariableSecretsProvider(envLogger);

            var akvUri = new Uri(options.AzureKeyVaultUri ?? throw new InvalidOperationException(
                "PpaSecretsOptions.AzureKeyVaultUri must be set for CI environment."));
            var fallback = new AzureKeyVaultProvider(akvUri, akvLogger);

            return new CompositeSecretsProvider(primary, fallback, logger);
        });
    }

    // Production: Azure Key Vault primary → HashiCorp Vault OSS fallback
    private static void RegisterProductionProviders(IServiceCollection services, PpaSecretsOptions options)
    {
        services.AddSingleton<ISecretsProvider>(sp =>
        {
            var logger = sp.GetRequiredService<ILogger<CompositeSecretsProvider>>();
            var akvLogger = sp.GetRequiredService<ILogger<AzureKeyVaultProvider>>();
            var vaultLogger = sp.GetRequiredService<ILogger<HashiCorpVaultProvider>>();

            var akvUri = new Uri(options.AzureKeyVaultUri ?? throw new InvalidOperationException(
                "PpaSecretsOptions.AzureKeyVaultUri must be set for Production environment."));
            var primary = new AzureKeyVaultProvider(akvUri, akvLogger);

            var fallback = new HashiCorpVaultProvider(
                new HashiCorpVaultOptions
                {
                    VaultAddress = options.HashiCorpVaultAddress ?? throw new InvalidOperationException(
                        "PpaSecretsOptions.HashiCorpVaultAddress must be set for Production environment."),
                    RoleId = options.ProdRoleId ?? throw new InvalidOperationException(
                        "PpaSecretsOptions.ProdRoleId must be set for Production environment."),
                    SecretId = options.ProdSecretId ?? throw new InvalidOperationException(
                        "PpaSecretsOptions.ProdSecretId must be set for Production environment.")
                },
                vaultLogger);

            return new CompositeSecretsProvider(primary, fallback, logger);
        });
    }

    private static bool IsCI() =>
        !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("CI")) ||
        !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("GITHUB_ACTIONS")) ||
        !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("TF_BUILD")); // Azure Pipelines
}

/// <summary>
/// Configuration options for the PPA dual-vault secrets provider.
/// Populate from environment variables, user-secrets, or IConfiguration — never hardcoded.
/// </summary>
public sealed class PpaSecretsOptions
{
    /// <summary>Azure Key Vault URI (e.g. "https://ppa-secrets.vault.azure.net/").</summary>
    public string? AzureKeyVaultUri { get; init; }

    /// <summary>HashiCorp Vault OSS base URL (e.g. "http://localhost:8200").</summary>
    public string? HashiCorpVaultAddress { get; init; }

    /// <summary>AppRole Role ID for local development.</summary>
    public string? DevRoleId { get; init; }

    /// <summary>AppRole Secret ID for local development (short-lived).</summary>
    public string? DevSecretId { get; init; }

    /// <summary>AppRole Role ID for production (corresponds to Entra-mapped service account).</summary>
    public string? ProdRoleId { get; init; }

    /// <summary>AppRole Secret ID for production (rotated per deployment).</summary>
    public string? ProdSecretId { get; init; }
}

/// <summary>
/// Resolves secrets from environment variables. Used as the primary provider in CI
/// and as a fallback in development (backed by dotnet user-secrets via IConfiguration).
/// </summary>
internal sealed class EnvironmentVariableSecretsProvider : ISecretsProvider
{
    private readonly ILogger<EnvironmentVariableSecretsProvider> _logger;

    public EnvironmentVariableSecretsProvider(ILogger<EnvironmentVariableSecretsProvider> logger)
        => _logger = logger;

    public Task<string?> GetAsync(string botId, string canonicalKey, CancellationToken cancellationToken = default)
    {
        var envKey = SecretNameTranslator.ToEnvVar(canonicalKey);
        var value = Environment.GetEnvironmentVariable(envKey);
        _logger.LogDebug("EnvVar: get — key={CanonicalKey} envKey={EnvKey} found={Found}",
            canonicalKey, envKey, value is not null);
        return Task.FromResult<string?>(value);
    }

    public async Task<SecretBundle> GetBundleAsync(
        string botId,
        System.Collections.Generic.IReadOnlyList<SecretDescriptor> descriptors,
        TimeSpan ttl,
        CancellationToken cancellationToken = default)
    {
        var secrets = new System.Collections.Generic.Dictionary<string, string>();
        var issuedAt = DateTimeOffset.UtcNow;

        foreach (var descriptor in descriptors)
        {
            var canonicalKey = SecretNameTranslator.ToCanonical(botId, descriptor.AppName, descriptor.CanonicalKey);
            var value = await GetAsync(botId, canonicalKey, cancellationToken);

            if (value is not null)
                secrets[canonicalKey] = value;
            else if (descriptor.Required)
                throw new SecretNotFoundException(botId, canonicalKey);
        }

        return new SecretBundle(botId, secrets, issuedAt, issuedAt.Add(ttl));
    }

    public Task<SecretBundle> RefreshAsync(
        SecretBundle expiredBundle,
        System.Collections.Generic.IReadOnlyList<SecretDescriptor> descriptors,
        TimeSpan ttl,
        CancellationToken cancellationToken = default)
        => GetBundleAsync(expiredBundle.BotId, descriptors, ttl, cancellationToken);
}
