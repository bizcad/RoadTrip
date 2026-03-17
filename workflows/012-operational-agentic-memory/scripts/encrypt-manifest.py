#!/usr/bin/env python3
"""
encrypt-manifest.py — JWE Manifest Encryption Utility

Takes an unencrypted secrets-manifest.json (key names only, no values)
and produces a secrets-manifest.enc file using JWE Compact Serialization (RFC 7516).

Algorithm: ECDH-ES+A256KW key agreement + A256GCM content encryption
This matches the SecretManifestResolver.cs decryption configuration.

Usage:
  # Encrypt using a local PEM key (local dev):
  python encrypt-manifest.py \\
    --input secrets-manifest.json \\
    --output secrets-manifest.enc \\
    --key-pem path/to/ec-key.pem

  # Encrypt using an Azure Key Vault EC key (CI/prod):
  python encrypt-manifest.py \\
    --input secrets-manifest.json \\
    --output secrets-manifest.enc \\
    --akv-key-id https://ppa-secrets.vault.azure.net/keys/manifest-key/VERSION

  # Verify decryption round-trip (local only):
  python encrypt-manifest.py \\
    --input secrets-manifest.json \\
    --output secrets-manifest.enc \\
    --key-pem path/to/ec-key.pem \\
    --verify

  # Generate a new local EC key pair for development:
  python encrypt-manifest.py --generate-key --key-output local-manifest-key.pem

Requirements:
  pip install joserfc cryptography azure-keyvault-keys azure-identity
"""

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s — %(message)s",
)
log = logging.getLogger("encrypt-manifest")


# ---------------------------------------------------------------------------
# Key loading
# ---------------------------------------------------------------------------

def load_ec_key_from_pem(pem_path: Path):
    """Load an EC private key from a local PEM file."""
    try:
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
    except ImportError:
        log.error("cryptography package required: pip install cryptography")
        sys.exit(1)

    if not pem_path.exists():
        log.error("PEM key file not found: %s", pem_path)
        sys.exit(1)

    with pem_path.open("rb") as f:
        return load_pem_private_key(f.read(), password=None)


def load_ec_public_key_from_akv(key_id: str):
    """Load the public key from Azure Key Vault for encryption (no private key needed for encryption)."""
    try:
        from azure.keyvault.keys import KeyClient
        from azure.keyvault.keys.crypto import CryptographyClient
        from azure.identity import DefaultAzureCredential
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    except ImportError:
        log.error("azure-keyvault-keys and azure-identity required: pip install azure-keyvault-keys azure-identity")
        sys.exit(1)

    credential = DefaultAzureCredential()
    # Parse vault URI from key ID: https://{vault}.vault.azure.net/keys/{name}/{version}
    parts = key_id.split("/")
    vault_uri = "/".join(parts[:3])
    key_name = parts[4]
    key_version = parts[5] if len(parts) > 5 else None

    client = KeyClient(vault_url=vault_uri, credential=credential)
    key = client.get_key(key_name, version=key_version)

    # Return the public key in JWK format for joserfc
    return key.key


# ---------------------------------------------------------------------------
# Encryption
# ---------------------------------------------------------------------------

def encrypt_manifest(plaintext_json: str, ec_private_key) -> str:
    """
    Encrypts the manifest JSON using JWE Compact Serialization.
    Algorithm: ECDH-ES+A256KW + A256GCM (RFC 7516)
    Returns the JWE compact token string.
    """
    try:
        from joserfc import jwe
        from joserfc.jwk import OctKey, ECKey
        from joserfc.rfc7517.asymmetric import ECKey as ECKeyType
    except ImportError:
        log.error("joserfc required: pip install joserfc")
        sys.exit(1)

    try:
        from cryptography.hazmat.primitives.serialization import (
            Encoding, PublicFormat, PrivateFormat, NoEncryption
        )

        # Export to JWK for joserfc
        public_key = ec_private_key.public_key()
        pub_pem = public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode()

        ec_key = ECKey.import_key({"pem": ec_private_key})
    except Exception as e:
        log.error("Key conversion failed: %s", e)
        sys.exit(1)

    protected = {
        "alg": "ECDH-ES+A256KW",
        "enc": "A256GCM",
    }

    try:
        token = jwe.encrypt_compact(
            protected,
            plaintext_json.encode("utf-8"),
            ec_key,
        )
    except Exception as e:
        log.error("JWE encryption failed: %s", e)
        sys.exit(1)

    return token.decode("utf-8") if isinstance(token, bytes) else token


def decrypt_manifest(jwe_compact: str, ec_private_key) -> str:
    """Decrypts a JWE compact token. Used for --verify round-trip check."""
    try:
        from joserfc import jwe
        from joserfc.jwk import ECKey
    except ImportError:
        log.error("joserfc required: pip install joserfc")
        sys.exit(1)

    ec_key = ECKey.import_key({"pem": ec_private_key})
    token = jwe.decrypt_compact(jwe_compact, ec_key)
    return token.plaintext.decode("utf-8")


# ---------------------------------------------------------------------------
# Key generation
# ---------------------------------------------------------------------------

def generate_ec_key(output_path: Path) -> None:
    """Generates a new P-256 EC key pair and writes it to a PEM file."""
    try:
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.serialization import (
            Encoding, PrivateFormat, NoEncryption, PublicFormat
        )
    except ImportError:
        log.error("cryptography required: pip install cryptography")
        sys.exit(1)

    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    public_pem = private_key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

    pub_path = output_path.with_suffix(".pub.pem")
    output_path.write_bytes(private_pem)
    pub_path.write_bytes(public_pem)

    log.info("Generated EC P-256 key pair:")
    log.info("  Private key: %s  (GITIGNORED — never commit this)", output_path)
    log.info("  Public key:  %s  (safe to commit for reference)", pub_path)
    log.info("")
    log.info("Add to .gitignore:  %s", output_path.name)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Encrypt/decrypt a PPA secrets manifest using JWE (RFC 7516).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--input", help="Path to unencrypted secrets-manifest.json")
    p.add_argument("--output", help="Path to write the encrypted secrets-manifest.enc")
    p.add_argument("--key-pem", help="Path to local EC private key PEM file")
    p.add_argument("--akv-key-id",
                   help="Azure Key Vault key ID for encryption (uses public key only)")
    p.add_argument("--verify", action="store_true",
                   help="After encrypting, decrypt and verify round-trip (requires --key-pem)")
    p.add_argument("--generate-key", action="store_true",
                   help="Generate a new EC P-256 key pair and exit")
    p.add_argument("--key-output", default="local-manifest-key.pem",
                   help="Output path for generated key (default: local-manifest-key.pem)")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.generate_key:
        generate_ec_key(Path(args.key_output))
        return

    if not args.input or not args.output:
        parser.error("--input and --output are required unless --generate-key is specified.")

    if not args.key_pem and not args.akv_key_id:
        parser.error("Provide either --key-pem (local dev) or --akv-key-id (CI/prod).")

    input_path = Path(args.input)
    if not input_path.exists():
        log.error("Input file not found: %s", input_path)
        sys.exit(1)

    plaintext = input_path.read_text(encoding="utf-8")

    # Validate JSON before encrypting
    try:
        parsed = json.loads(plaintext)
        if "value" in str(parsed):
            # Extra safety check: warn if the manifest appears to contain values
            log.warning(
                "WARNING: The manifest appears to contain 'value' fields. "
                "Ensure you are encrypting a key-names-only manifest, not a manifest with secret values."
            )
    except json.JSONDecodeError as e:
        log.error("Input file is not valid JSON: %s", e)
        sys.exit(1)

    if args.key_pem:
        ec_key = load_ec_key_from_pem(Path(args.key_pem))
    else:
        ec_key = load_ec_public_key_from_akv(args.akv_key_id)

    log.info("Encrypting manifest: %s → %s", args.input, args.output)
    jwe_compact = encrypt_manifest(plaintext, ec_key)

    output_path = Path(args.output)
    output_path.write_text(jwe_compact, encoding="utf-8")
    log.info("Encrypted manifest written: %s (%d bytes)", output_path, len(jwe_compact))

    if args.verify:
        if not args.key_pem:
            log.warning("--verify requires --key-pem (private key). Skipping verification.")
        else:
            log.info("Verifying round-trip decryption...")
            decrypted = decrypt_manifest(jwe_compact, ec_key)
            if json.loads(decrypted) == json.loads(plaintext):
                log.info("Round-trip verification: PASSED")
            else:
                log.error("Round-trip verification: FAILED — decrypted content does not match input")
                sys.exit(1)


if __name__ == "__main__":
    main()
