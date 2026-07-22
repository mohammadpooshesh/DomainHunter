from __future__ import annotations

import socket
import ssl as ssl_lib
from datetime import datetime, timezone
from typing import Any, Optional

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend

from config import Config


class SSLModule:
    name = "ssl"

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {}
        try:
            cert_info = self._get_certificate(domain, config.timeout)
            if cert_info:
                result.update(cert_info)
            tls_info = self._get_tls_version(domain, config.timeout)
            if tls_info:
                result.update(tls_info)
        except Exception as e:
            result["error"] = str(e)
        return result

    def _get_certificate(self, domain: str, timeout: int) -> Optional[dict[str, Any]]:
        try:
            context = ssl_lib.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl_lib.CERT_NONE
            with socket.create_connection((domain, 443), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    der_cert = ssock.getpeercert(binary_form=True)
                    if not der_cert:
                        return None
                    cert = x509.load_der_x509_certificate(der_cert, default_backend())
                    cipher = ssock.cipher()
                    cert_info: dict[str, Any] = {}
                    try:
                        cert_info["subject"] = str(cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value)
                    except (IndexError, ValueError):
                        cert_info["subject"] = str(cert.subject)
                    try:
                        cert_info["issuer"] = str(cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value)
                    except (IndexError, ValueError):
                        cert_info["issuer"] = str(cert.issuer)
                    cert_info["serial"] = str(cert.serial_number)
                    cert_info["version"] = cert.version.value
                    cert_info["not_before"] = cert.not_valid_before_utc.strftime("%Y-%m-%d %H:%M:%S")
                    cert_info["not_after"] = cert.not_valid_after_utc.strftime("%Y-%m-%d %H:%M:%S")
                    days_left = (cert.not_valid_after_utc - datetime.now(timezone.utc)).days
                    cert_info["days_remaining"] = days_left
                    try:
                        san_ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                        cert_info["san"] = [str(name) for name in san_ext.value]
                    except x509.ExtensionNotFound:
                        cert_info["san"] = []
                    chain: list[str] = []
                    try:
                        for ca in ssock.get_verified_chain():
                            ca_cert = x509.load_der_x509_certificate(ca, default_backend())
                            try:
                                cn = ca_cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
                                chain.append(str(cn))
                            except (IndexError, ValueError):
                                chain.append(str(ca_cert.subject))
                    except Exception:
                        pass
                    cert_info["chain"] = chain
                    cert_info["cipher"] = cipher[0] if cipher else None
                    cert_info["tls_version"] = ssock.version()
                    return cert_info
        except (socket.timeout, ConnectionRefusedError, ConnectionResetError, OSError, ssl_lib.SSLError):
            return None

    def _get_tls_version(self, domain: str, timeout: int) -> dict[str, Any]:
        versions: dict[str, Any] = {}
        tls_methods = {
            "TLS 1.0": ssl_lib.PROTOCOL_TLSv1,
            "TLS 1.1": ssl_lib.PROTOCOL_TLSv1_1,
            "TLS 1.2": ssl_lib.PROTOCOL_TLSv1_2,
        }
        available: list[str] = []
        for name, method in tls_methods.items():
            try:
                context = ssl_lib.SSLContext(method)
                context.check_hostname = False
                context.verify_mode = ssl_lib.CERT_NONE
                with socket.create_connection((domain, 443), timeout=timeout) as sock:
                    with context.wrap_socket(sock, server_hostname=domain):
                        available.append(name)
            except (ssl_lib.SSLError, socket.timeout, ConnectionError, OSError):
                pass
        versions["supported_versions"] = available
        return versions
