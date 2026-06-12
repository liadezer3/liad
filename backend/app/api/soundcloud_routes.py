from __future__ import annotations

import secrets
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.config import settings
from app.services.network import (
    frontend_origin_from_request,
    mobile_access_info,
    resolve_redirect_uri,
)
from app.services.soundcloud import (
    SoundCloudClient,
    build_authorize_url,
    exchange_code,
    generate_pkce_pair,
    pick_stream_url,
    refresh_access_token,
    sign_out,
    token_expires_at,
)

router = APIRouter(tags=["soundcloud"])


def _configured() -> bool:
    return bool(settings.soundcloud_client_id and settings.soundcloud_client_secret)


async def _get_client(request: Request) -> SoundCloudClient:
    session = request.session
    access_token = session.get("access_token")
    refresh = session.get("refresh_token")
    expires_at = session.get("expires_at", 0)

    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated. Connect your SoundCloud account.")

    if refresh and expires_at and time_before_expiry(expires_at):
        try:
            tokens = await refresh_access_token(refresh)
            session["access_token"] = tokens["access_token"]
            session["refresh_token"] = tokens.get("refresh_token", refresh)
            session["expires_at"] = token_expires_at(tokens.get("expires_in", 3600))
            access_token = tokens["access_token"]
        except Exception as exc:
            raise HTTPException(status_code=401, detail="Session expired. Please sign in again.") from exc

    return SoundCloudClient(access_token)


def time_before_expiry(expires_at: float) -> bool:
    import time

    return time.time() >= expires_at


@router.get("/auth/status")
def auth_status(request: Request) -> dict[str, Any]:
    return {
        "configured": _configured(),
        "authenticated": bool(request.session.get("access_token")),
    }


@router.get("/network-info")
def network_info() -> dict[str, str | None]:
    return mobile_access_info()


@router.get("/auth/login")
def login(request: Request) -> RedirectResponse:
    if not _configured():
        raise HTTPException(
            status_code=503,
            detail="SoundCloud API credentials are not configured. Set SOUNDCLOUD_CLIENT_ID and SOUNDCLOUD_CLIENT_SECRET.",
        )

    frontend_origin = frontend_origin_from_request(
        request.headers.get("origin"),
        request.headers.get("referer"),
    )
    try:
        redirect_uri = resolve_redirect_uri(frontend_origin)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    verifier, challenge = generate_pkce_pair()
    state = secrets.token_urlsafe(24)
    request.session["oauth_state"] = state
    request.session["pkce_verifier"] = verifier
    request.session["frontend_origin"] = frontend_origin
    request.session["redirect_uri"] = redirect_uri
    return RedirectResponse(build_authorize_url(state, challenge, redirect_uri))


@router.get("/auth/callback")
async def callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    frontend_origin = request.session.get("frontend_origin", settings.frontend_url)
    if error:
        return RedirectResponse(f"{frontend_origin}/?auth_error={error}")

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    if state != request.session.get("oauth_state"):
        raise HTTPException(status_code=400, detail="Invalid OAuth state.")

    verifier = request.session.pop("pkce_verifier", None)
    request.session.pop("oauth_state", None)
    if not verifier:
        raise HTTPException(status_code=400, detail="OAuth session expired.")

    redirect_uri = request.session.get("redirect_uri", settings.soundcloud_redirect_uri)
    tokens = await exchange_code(code, verifier, redirect_uri)
    request.session["access_token"] = tokens["access_token"]
    request.session["refresh_token"] = tokens.get("refresh_token")
    request.session["expires_at"] = token_expires_at(tokens.get("expires_in", 3600))
    request.session.pop("frontend_origin", None)
    request.session.pop("redirect_uri", None)
    return RedirectResponse(f"{frontend_origin}/")


@router.post("/auth/logout")
async def logout(request: Request) -> dict[str, str]:
    token = request.session.get("access_token")
    if token:
        try:
            await sign_out(token)
        except Exception:
            pass
    request.session.clear()
    return {"status": "signed_out"}


@router.get("/me")
async def me(request: Request) -> dict[str, Any]:
    client = await _get_client(request)
    profile = await client.get_me()
    return {
        "id": profile.get("id"),
        "username": profile.get("username"),
        "full_name": profile.get("full_name") or profile.get("username"),
        "avatar_url": profile.get("avatar_url"),
        "permalink_url": profile.get("permalink_url"),
    }


@router.get("/playlists")
async def playlists(request: Request) -> list[dict[str, Any]]:
    client = await _get_client(request)
    items = await client.get_playlists()
    return [
        {
            "id": p.get("id"),
            "title": p.get("title"),
            "description": p.get("description"),
            "artwork_url": p.get("artwork_url"),
            "track_count": p.get("track_count") or len(p.get("tracks") or []),
            "permalink_url": p.get("permalink_url"),
        }
        for p in items
    ]


@router.get("/playlists/{playlist_id}")
async def playlist_detail(playlist_id: int, request: Request) -> dict[str, Any]:
    client = await _get_client(request)
    data = await client.get_playlist(playlist_id)
    tracks = []
    for track in data.get("tracks") or []:
        if not track:
            continue
        tracks.append(
            {
                "id": track.get("id"),
                "title": track.get("title"),
                "artist": (track.get("user") or {}).get("username", "Unknown"),
                "duration_ms": track.get("duration"),
                "artwork_url": track.get("artwork_url") or (track.get("user") or {}).get("avatar_url"),
                "permalink_url": track.get("permalink_url"),
                "access": track.get("access", "playable"),
            }
        )
    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "description": data.get("description"),
        "artwork_url": data.get("artwork_url"),
        "permalink_url": data.get("permalink_url"),
        "tracks": tracks,
    }


@router.get("/tracks/{track_id}/stream")
async def track_stream(track_id: int, request: Request) -> dict[str, Any]:
    client = await _get_client(request)
    try:
        streams = await client.get_track_streams(track_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Track is not available for streaming.") from exc

    url = pick_stream_url(streams)
    if not url:
        raise HTTPException(status_code=404, detail="No stream URL available for this track.")

    return {"stream_url": url, "is_preview": "preview" in url}
