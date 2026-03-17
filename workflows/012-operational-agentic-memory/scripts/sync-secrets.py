#!/usr/bin/env python3
"""
sync-secrets.py — PPA Secrets Plane Sync Script

Reads a local (unencrypted) secrets-manifest.json that includes secret VALUES,
then pushes those values to one or more target vaults/platforms.

IMPORTANT SECURITY RULES:
  - This script must NEVER be committed to source control with actual values.
  - The input file (secrets-manifest-with-values.json) must be gitignored.
  - This script NEVER logs secret values — only canonical key names and targets.
  - Secret values in memory only; no disk writes beyond what the SDKs do internally.

Usage:
  python sync-secrets.py --manifest secrets-manifest-with-values.json \\
    --akv                           \\   # Push to Azure Key Vault
    --vault                         \\   # Push to HashiCorp Vault OSS
    [--github OWNER/REPO]           \\   # Push to GitHub Secrets
    [--vercel PROJECT_ID]           \\   # Push to Vercel env vars
    [--env production|preview|development]  # Vercel target env (default: production)
    [--dry-run]                          # Print what would be done, no writes

Requirements:
  pip install azure-keyvault-secrets azure-identity hvac PyGithub requests
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

# Configure logging — secret values must NEVER appear in log output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)
log = logging.getLogger("sync-secrets")


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------

def load_manifest(path: Path) -> dict[str, Any]:
    """Load and validate the unencrypted manifest (with values) from disk."""
    if not path.exists():
        log.error("Manifest file not found: %s", path)
        sys.exit(1)

    with path.open() as f:
        manifest = json.load(f)

    required_fields = ("bot_id", "version", "secrets")
    for field in required_fields:
        if field not in manifest:
            log.error("Manifest missing required field: %s", field)
            sys.exit(1)

    return manifest


def get_secret_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Returns entries that have a 'value' field set (non-empty)."""
    entries = []
    for entry in manifest.get("secrets", []):
        if "value" not in entry or not entry["value"]:
            log.warning("Skipping entry with no value: app_name=%s key=%s",
                        entry.get("app_name"), entry.get("key"))
        else:
            entries.append(entry)
    return entries


# ---------------------------------------------------------------------------
# Canonical name translation (mirrors SecretNameTranslator.cs)
# ---------------------------------------------------------------------------

def to_canonical(bot_id: str, app_name: str, key: str) -> str:
    """Build the canonical key name: BOT_NAME__APP_NAME__KEY_NAME."""
    def normalize(s: str) -> str:
        return s.strip().upper().replace("-", "_")
    return f"{normalize(bot_id)}__{normalize(app_name)}__{normalize(key)}"


def to_akv_name(canonical: str) -> str:
    """LEGAL_BOT__WESTLAW__WESTLAW_API_KEY → legal-bot--westlaw--westlaw-api-key"""
    return canonical.replace("__", "--").replace("_", "-").lower()


def to_vault_path(canonical: str) -> str:
    """LEGAL_BOT__WESTLAW__WESTLAW_API_KEY → legal-bot/westlaw/WESTLAW_API_KEY"""
    parts = canonical.split("__", 2)
    if len(parts) != 3:
        return canonical.lower().replace("__", "/")
    bot = parts[0].lower().replace("_", "-")
    app = parts[1].lower().replace("_", "-")
    key = parts[2]  # preserve casing for key
    return f"{bot}/{app}/{key}"


def to_env_var(canonical: str) -> str:
    """Canonical → UPPER_SNAKE_CASE (no change needed)."""
    return canonical.upper()


# ---------------------------------------------------------------------------
# Azure Key Vault
# ---------------------------------------------------------------------------

def push_to_akv(entries: list[dict], bot_id: str, vault_uri: str, dry_run: bool) -> None:
    try:
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential
    except ImportError:
        log.error("azure-keyvault-secrets and azure-identity are required: pip install azure-keyvault-secrets azure-identity")
        sys.exit(1)

    client = SecretClient(vault_url=vault_uri, credential=DefaultAzureCredential())

    for entry in entries:
        canonical = to_canonical(bot_id, entry["app_name"], entry["key"])
        akv_name = to_akv_name(canonical)

        if dry_run:
            log.info("[DRY-RUN] AKV set: %s → %s", canonical, akv_name)
        else:
            client.set_secret(akv_name, entry["value"])
            log.info("AKV set: %s → %s", canonical, akv_name)


# ---------------------------------------------------------------------------
# HashiCorp Vault OSS
# ---------------------------------------------------------------------------

def push_to_hashicorp_vault(
    entries: list[dict], bot_id: str,
    vault_addr: str, token: str, mount: str, dry_run: bool
) -> None:
    try:
        import hvac
    except ImportError:
        log.error("hvac is required: pip install hvac")
        sys.exit(1)

    client = hvac.Client(url=vault_addr, token=token)
    if not client.is_authenticated():
        log.error("HashiCorp Vault authentication failed. Check VAULT_TOKEN.")
        sys.exit(1)

    for entry in entries:
        canonical = to_canonical(bot_id, entry["app_name"], entry["key"])
        vault_path = to_vault_path(canonical)
        # KV v2: split path into mount + sub-path
        path_parts = vault_path.split("/", 1)
        sub_path = path_parts[1] if len(path_parts) == 2 else vault_path

        if dry_run:
            log.info("[DRY-RUN] Vault set: %s → %s/data/%s", canonical, mount, sub_path)
        else:
            client.secrets.kv.v2.create_or_update_secret(
                mount_point=mount,
                path=sub_path,
                secret={"value": entry["value"]},
            )
            log.info("Vault set: %s → %s/data/%s", canonical, mount, sub_path)


# ---------------------------------------------------------------------------
# GitHub Secrets
# ---------------------------------------------------------------------------

def push_to_github(
    entries: list[dict], bot_id: str, repo_slug: str, dry_run: bool
) -> None:
    try:
        from github import Github, GithubException
    except ImportError:
        log.error("PyGithub is required: pip install PyGithub")
        sys.exit(1)

    import os
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        log.error("GITHUB_TOKEN environment variable is not set.")
        sys.exit(1)

    g = Github(token)
    repo = g.get_repo(repo_slug)

    for entry in entries:
        canonical = to_canonical(bot_id, entry["app_name"], entry["key"])
        secret_name = canonical.upper().replace("-", "_")  # GitHub: UPPER_SNAKE, no dashes

        if dry_run:
            log.info("[DRY-RUN] GitHub secret set: %s → %s/%s", canonical, repo_slug, secret_name)
        else:
            repo.create_secret(secret_name, entry["value"])
            log.info("GitHub secret set: %s → %s/%s", canonical, repo_slug, secret_name)


# ---------------------------------------------------------------------------
# Vercel Environment Variables
# ---------------------------------------------------------------------------

def push_to_vercel(
    entries: list[dict], bot_id: str,
    project_id: str, env_target: str, dry_run: bool
) -> None:
    import os
    import requests

    token = os.environ.get("VERCEL_TOKEN")
    if not token:
        log.error("VERCEL_TOKEN environment variable is not set.")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    for entry in entries:
        canonical = to_canonical(bot_id, entry["app_name"], entry["key"])
        env_key = to_env_var(canonical)

        payload = {
            "key": env_key,
            "value": entry["value"],  # never logged
            "type": "encrypted",
            "target": [env_target],
        }

        if dry_run:
            log.info("[DRY-RUN] Vercel env set: %s → project=%s target=%s", canonical, project_id, env_target)
        else:
            resp = requests.post(
                f"https://api.vercel.com/v9/projects/{project_id}/env",
                headers=headers,
                json=payload,
                timeout=15,
            )
            if resp.status_code in (200, 201):
                log.info("Vercel env set: %s → project=%s target=%s", canonical, project_id, env_target)
            elif resp.status_code == 409:
                # Already exists — patch instead
                resp2 = requests.patch(
                    f"https://api.vercel.com/v9/projects/{project_id}/env/{env_key}",
                    headers=headers,
                    json={"value": entry["value"], "type": "encrypted", "target": [env_target]},
                    timeout=15,
                )
                resp2.raise_for_status()
                log.info("Vercel env updated: %s", canonical)
            else:
                resp.raise_for_status()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Sync PPA secrets from a local manifest to configured vaults and platforms.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--manifest", required=True,
                   help="Path to the unencrypted secrets-manifest-with-values.json (gitignored)")
    p.add_argument("--akv", action="store_true",
                   help="Push to Azure Key Vault (requires AKV_VAULT_URI env var)")
    p.add_argument("--vault", action="store_true",
                   help="Push to HashiCorp Vault OSS (requires VAULT_ADDR and VAULT_TOKEN env vars)")
    p.add_argument("--vault-mount", default="secret",
                   help="HashiCorp Vault KV v2 mount path (default: secret)")
    p.add_argument("--github",
                   help="Push to GitHub Secrets for OWNER/REPO (requires GITHUB_TOKEN)")
    p.add_argument("--vercel",
                   help="Push to Vercel env vars for PROJECT_ID (requires VERCEL_TOKEN)")
    p.add_argument("--env", default="production",
                   choices=["production", "preview", "development"],
                   help="Vercel target environment (default: production)")
    p.add_argument("--dry-run", action="store_true",
                   help="Print what would be done without making any changes")
    return p


def main() -> None:
    import os

    parser = build_parser()
    args = parser.parse_args()

    if args.dry_run:
        log.info("=== DRY-RUN MODE: no secrets will be written ===")

    manifest = load_manifest(Path(args.manifest))
    bot_id = manifest["bot_id"]
    entries = get_secret_entries(manifest)

    log.info("Loaded manifest: bot_id=%s version=%s secrets=%d",
             bot_id, manifest.get("version"), len(entries))

    if not entries:
        log.warning("No secrets with values found in manifest. Nothing to sync.")
        return

    if args.akv:
        vault_uri = os.environ.get("AKV_VAULT_URI")
        if not vault_uri:
            log.error("AKV_VAULT_URI environment variable is not set.")
            sys.exit(1)
        log.info("Syncing %d secrets to Azure Key Vault (%s)...", len(entries), vault_uri)
        push_to_akv(entries, bot_id, vault_uri, args.dry_run)

    if args.vault:
        vault_addr = os.environ.get("VAULT_ADDR", "http://localhost:8200")
        vault_token = os.environ.get("VAULT_TOKEN")
        if not vault_token:
            log.error("VAULT_TOKEN environment variable is not set.")
            sys.exit(1)
        log.info("Syncing %d secrets to HashiCorp Vault (%s)...", len(entries), vault_addr)
        push_to_hashicorp_vault(entries, bot_id, vault_addr, vault_token, args.vault_mount, args.dry_run)

    if args.github:
        log.info("Syncing %d secrets to GitHub Secrets (%s)...", len(entries), args.github)
        push_to_github(entries, bot_id, args.github, args.dry_run)

    if args.vercel:
        log.info("Syncing %d secrets to Vercel (%s, env=%s)...", len(entries), args.vercel, args.env)
        push_to_vercel(entries, bot_id, args.vercel, args.env, args.dry_run)

    if not any([args.akv, args.vault, args.github, args.vercel]):
        log.warning("No target specified. Use --akv, --vault, --github, and/or --vercel.")

    log.info("Sync complete.")


if __name__ == "__main__":
    main()
