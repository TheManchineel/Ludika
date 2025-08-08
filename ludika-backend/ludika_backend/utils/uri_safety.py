import socket
from ipaddress import ip_address
from urllib.parse import urlparse


def is_private_ip(uri: str) -> bool:
    try:
        result = urlparse(uri)
        hostname = result.hostname
        if not hostname:
            return False
        ip = socket.gethostbyname(hostname)
        return ip_address(ip).is_private
    except Exception:
        return False
