from __future__ import annotations

import socket
from typing import Any

import dns.resolver
from dns.exception import DNSException

from config import Config


class PortScanModule:
    name = "portscan"

    COMMON_PORTS = [
        21, 22, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995,
        1433, 1521, 2049, 2375, 2376, 3306, 3389, 5432, 5900,
        6379, 8080, 8443, 9000, 9200, 27017,
    ]

    SERVICE_MAP: dict[int, str] = {
        21: "FTP", 22: "SSH", 25: "SMTP", 53: "DNS", 80: "HTTP",
        110: "POP3", 143: "IMAP", 443: "HTTPS", 465: "SMTPS",
        587: "SMTP Submission", 993: "IMAPS", 995: "POP3S",
        1433: "MSSQL", 1521: "Oracle DB", 2049: "NFS",
        2375: "Docker (unencrypted)", 2376: "Docker (TLS)",
        3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
        5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt",
        8443: "HTTPS-Alt", 9000: "Portainer", 9200: "Elasticsearch",
        27017: "MongoDB",
    }

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {"open_ports": [], "total_open": 0}
        ips = self._get_ips(domain)
        if not ips:
            result["error"] = "Could not resolve domain IP"
            return result

        ip = ips[0]
        result["target_ip"] = ip
        open_ports: list[dict[str, Any]] = []
        for port in self.COMMON_PORTS:
            if self._check_port(ip, port, config.timeout):
                service = self.SERVICE_MAP.get(port, "Unknown")
                banner = self._grab_banner(ip, port, config.timeout)
                open_ports.append({
                    "port": port,
                    "service": service,
                    "banner": banner,
                })
        result["open_ports"] = open_ports
        result["total_open"] = len(open_ports)
        return result

    def _get_ips(self, domain: str) -> list[str]:
        ips: list[str] = []
        try:
            answers = dns.resolver.resolve(domain, "A", lifetime=10)
            ips = [str(r) for r in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, DNSException):
            pass
        return ips

    def _check_port(self, ip: str, port: int, timeout: int) -> bool:
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def _grab_banner(self, ip: str, port: int, timeout: int) -> str:
        try:
            with socket.create_connection((ip, port), timeout=timeout) as sock:
                sock.settimeout(timeout)
                if port in {21, 22, 25, 80, 110, 143, 443, 587, 993, 995, 8080, 8443}:
                    try:
                        data = sock.recv(1024)
                        banner = data.decode("utf-8", errors="ignore").strip()
                        return banner[:200]
                    except (socket.timeout, ConnectionError):
                        pass
                if port == 80:
                    sock.sendall(f"GET / HTTP/1.0\r\nHost: {ip}\r\n\r\n".encode())
                    try:
                        data = sock.recv(1024)
                        return data.decode("utf-8", errors="ignore").split("\r\n")[0][:200]
                    except (socket.timeout, ConnectionError):
                        pass
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass
        return ""
