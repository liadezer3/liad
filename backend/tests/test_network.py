import pytest

from app.services.network import frontend_origin_from_request, resolve_redirect_uri


def test_frontend_origin_from_referer(monkeypatch):
    monkeypatch.setattr(
        "app.services.network.settings.frontend_url",
        "http://localhost:5173",
    )
    origin = frontend_origin_from_request(
        None,
        "http://192.168.1.42:5173/login",
    )
    assert origin == "http://192.168.1.42:5173"


def test_resolve_redirect_uri_matches_frontend(monkeypatch):
    monkeypatch.setattr(
        "app.services.network.settings.soundcloud_redirect_uris",
        "http://127.0.0.1:5173/api/auth/callback,http://192.168.1.42:5173/api/auth/callback",
    )
    monkeypatch.setattr("app.services.network.settings.soundcloud_redirect_uri", "")
    uri = resolve_redirect_uri("http://192.168.1.42:5173")
    assert uri == "http://192.168.1.42:5173/api/auth/callback"


def test_resolve_redirect_uri_unknown_raises(monkeypatch):
    monkeypatch.setattr(
        "app.services.network.settings.soundcloud_redirect_uris",
        "http://127.0.0.1:5173/api/auth/callback",
    )
    monkeypatch.setattr("app.services.network.settings.soundcloud_redirect_uri", "")
    with pytest.raises(ValueError):
        resolve_redirect_uri("http://192.168.1.99:5173")
