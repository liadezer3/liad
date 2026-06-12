from __future__ import annotations

import socket
from urllib.parse import urlparse

from app.config import settings


def get_lan_ip() -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return None


def configured_redirect_uris() -> list[str]:
    raw = settings.soundcloud_redirect_uris or settings.soundcloud_redirect_uri
    return [uri.strip() for uri in raw.split(",") if uri.strip()]


def frontend_origin_from_request(origin: str | None, referer: str | None) -> str:
    if origin:
        return origin.rstrip("/")
    if referer:
        parsed = urlparse(referer)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
    return settings.frontend_url.rstrip("/")


def resolve_redirect_uri(frontend_origin: str) -> str:
    candidate = f"{frontend_origin.rstrip('/')}/api/auth/callback"
    allowed = configured_redirect_uris()
    if candidate in allowed:
        return candidate
    raise ValueError(
        f"Redirect URI {candidate} is not registered. "
        f"Add it to SOUNDCLOUD_REDIRECT_URIS in backend/.env and to your SoundCloud app."
    )


def mobile_access_info(port: int = 5173) -> dict[str, str | None]:
    lan_ip = get_lan_ip()
    if not lan_ip:
        return {"lan_ip": None, "mobile_url": None, "redirect_uri_hint": None}
    mobile_url = f"http://{lan_ip}:{port}"
    return {
        "lan_ip": lan_ip,
        "mobile_url": mobile_url,
        "redirect_uri_hint": f"{mobile_url}/api/auth/callback",
    }
