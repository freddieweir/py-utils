#!/usr/bin/env python3
"""
ssl_setup.py

A module to generate self-signed SSL certificates and provide SSL contexts for HTTPS.
"""
import os
import ssl
import datetime
from pathlib import Path

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
except ImportError as e:
    raise ImportError("cryptography library is required: install with 'pip install cryptography'") from e

class SSLManager:
    """
    Manage generation and loading of SSL certificates for HTTPS.
    """
    def __init__(self, common_name: str = "localhost", cert_dir: str = None, valid_days: int = 3650, key_size: int = 2048):
        """
        Initialize SSLManager.

        Args:
            common_name: The domain name for the certificate (e.g., 'localhost').
            cert_dir: Directory to store certificates (defaults to '~/.py_utils/certs').
            valid_days: Number of days the certificate is valid.
            key_size: RSA key size in bits.
        """
        self.common_name = common_name
        self.valid_days = valid_days
        self.key_size = key_size
        
        # Determine certificate directory
        if cert_dir:
            self.cert_dir = Path(cert_dir).expanduser().resolve()
        else:
            self.cert_dir = Path.home() / ".py_utils" / "certs"
        self.cert_dir.mkdir(parents=True, exist_ok=True)

        self.key_path = self.cert_dir / f"{self.common_name}.key.pem"
        self.cert_path = self.cert_dir / f"{self.common_name}.cert.pem"

    def ensure_certificate(self):
        """
        Ensure a valid certificate exists; generate a new one if not present.
        """
        if self.key_path.exists() and self.cert_path.exists():
            # TODO: Check expiration if needed
            return
        self.generate_self_signed_cert()

    def generate_self_signed_cert(self):
        """
        Generate a self-signed certificate and private key.
        """
        # Generate private key
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size,
            backend=default_backend()
        )

        # Build certificate subject and issuer
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, self.common_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Local Development"),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=self.valid_days)
            )
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName(self.common_name)]),
                critical=False,
            )
            .sign(key, hashes.SHA256(), default_backend())
        )

        # Write key to file
        with open(self.key_path, "wb") as f:
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        # Write certificate to file
        with open(self.cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

    def get_ssl_context(self) -> ssl.SSLContext:
        """
        Load or generate the certificate and return an SSLContext for HTTPS.

        Returns:
            An ssl.SSLContext configured with the generated certificate.
        """
        self.ensure_certificate()
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=str(self.cert_path), keyfile=str(self.key_path))
        return context


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a self-signed SSL certificate for HTTPS"
    )
    parser.add_argument(
        "--common-name", "-n", default="localhost",
        help="Common Name (CN) for the certificate"
    )
    parser.add_argument(
        "--cert-dir", "-d", default=None,
        help="Directory to store certificates"
    )
    args = parser.parse_args()

    manager = SSLManager(
        common_name=args.common_name,
        cert_dir=args.cert_dir
    )
    manager.generate_self_signed_cert()
    print(f"Generated key at {manager.key_path}")
    print(f"Generated certificate at {manager.cert_path}")
