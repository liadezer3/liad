from __future__ import annotations

import base64
import hashlib
import secrets
import time
from typing import Any
from urllib.parse import urlencode

import httpx

from app.config import settings

SOUNDCLOUD_API = "https://api.soundcloud.com"
SOUNDCLOUD_AUTH = "https://secure.soundcloud.com"


def generate_pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)[:128]
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
        .decode("ascii")
        .rstrip("=")
    )
    return verifier, challenge


def build_authorize_url(state: str, code_challenge: str) -> str:
    params = {
        "client_id": settings.soundcloud_client_id,
        "redirect_uri": settings.soundcloud_redirect_uri,
        "response_type": "code",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    return f"{SOUNDCLOUD_AUTH}/authorize?{urlencode(params)}"


class SoundCloudClient:
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self._headers = {
            "accept": "application/json; charset=utf-8",
            "Authorization": f"OAuth {access_token}",
        }

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{SOUNDCLOUD_API}{path}" if path.startswith("/") else path
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(method, url, headers=self._headers, **kwargs)
            response.raise_for_status()
            if response.content:
                return response.json()
            return None

    async def get_me(self) -> dict[str, Any]:
        return await self._request("GET", "/me")

    async def get_playlists(self, limit: int = 50) -> list[dict[str, Any]]:
        data = await self._request(
            "GET",
            "/me/playlists",
            params={"show_tracks": "false", "linked_partitioning": "true", "limit": limit},
        )
        return _collect_collection(data)

    async def get_playlist(self, playlist_id: int) -> dict[str, Any]:
        return await self._request(
            "GET",
            f"/playlists/{playlist_id}",
            params={"show_tracks": "true"},
        )

    async def get_track_streams(self, track_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/tracks/{track_id}/streams")

    async def resolve_url(self, url: str) -> dict[str, Any]:
        return await self._request("GET", "/resolve", params={"url": url})


async def exchange_code(code: str, code_verifier: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{SOUNDCLOUD_AUTH}/oauth/token",
            headers={
                "accept": "application/json; charset=utf-8",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "authorization_code",
                "client_id": settings.soundcloud_client_id,
                "client_secret": settings.soundcloud_client_secret,
                "redirect_uri": settings.soundcloud_redirect_uri,
                "code_verifier": code_verifier,
                "code": code,
            },
        )
        response.raise_for_status()
        return response.json()


async def refresh_access_token(refresh_token: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{SOUNDCLOUD_AUTH}/oauth/token",
            headers={
                "accept": "application/json; charset=utf-8",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "refresh_token",
                "client_id": settings.soundcloud_client_id,
                "client_secret": settings.soundcloud_client_secret,
                "refresh_token": refresh_token,
            },
        )
        response.raise_for_status()
        return response.json()


async def sign_out(access_token: str) -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        await client.post(
            f"{SOUNDCLOUD_AUTH}/sign-out",
            headers={"Content-Type": "application/json"},
            json={"access_token": access_token},
        )


def token_expires_at(expires_in: int) -> float:
    return time.time() + max(expires_in - 60, 0)


def pick_stream_url(streams: dict[str, Any]) -> str | None:
    for key in ("hls_aac_160_url", "hls_aac_96_url", "http_mp3_128_url", "preview_mp3_128_url"):
        url = streams.get(key)
        if url:
            return url
    return None


def _collect_collection(data: dict[str, Any] | list[Any]) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return data

    items = list(data.get("collection", []))
    next_href = data.get("next_href")
    return items
