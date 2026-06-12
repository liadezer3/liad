from app.services.soundcloud import generate_pkce_pair, pick_stream_url


def test_pkce_pair_is_valid():
    verifier, challenge = generate_pkce_pair()
    assert 43 <= len(verifier) <= 128
    assert challenge
    assert "=" not in challenge


def test_pick_stream_url_prefers_hls_aac():
    streams = {
        "preview_mp3_128_url": "https://example.com/preview.mp3",
        "hls_aac_96_url": "https://example.com/96.m3u8",
        "hls_aac_160_url": "https://example.com/160.m3u8",
    }
    assert pick_stream_url(streams) == "https://example.com/160.m3u8"


def test_pick_stream_url_falls_back_to_preview():
    streams = {"preview_mp3_128_url": "https://example.com/preview.mp3"}
    assert pick_stream_url(streams) == "https://example.com/preview.mp3"
