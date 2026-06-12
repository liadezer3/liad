# Wavebox — SoundCloud Playlist Player

A clean, ad-free web player for your SoundCloud playlists. Connect your account, pick a playlist, and listen without banners or interruptions.

## How it works

Wavebox uses the official [SoundCloud API](https://developers.soundcloud.com/docs/api/guide) with OAuth 2.1. Your playlists and tracks are fetched through the API, and audio is streamed directly via HLS — not through SoundCloud's embedded widget — so you get a distraction-free listening experience.

## Setup

### 1. Register a SoundCloud app

1. Sign in at [soundcloud.com/you/apps](https://soundcloud.com/you/apps) (Artist Pro may be required).
2. Create an app and note your **Client ID** and **Client Secret**.
3. Add redirect URIs (desktop + phone on same Wi‑Fi):
   - `http://127.0.0.1:5173/api/auth/callback`
   - `http://YOUR_LAN_IP:5173/api/auth/callback` (replace with your computer's local IP)

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your SoundCloud credentials
chmod +x run.sh && ./run.sh
```

API: http://127.0.0.1:8000

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

Vite exposes the app on your local network too — check the terminal for a `Network:` URL like `http://192.168.x.x:5173`.

### Listen on your phone

1. Connect your phone to the **same Wi‑Fi** as your computer.
2. Start backend and frontend as above.
3. On the login screen, Wavebox shows your phone URL (or use the `Network:` address from the Vite terminal).
4. Register the phone redirect URI in SoundCloud, e.g. `http://192.168.1.42:5173/api/auth/callback`.
5. Add the same URI to `SOUNDCLOUD_REDIRECT_URIS` in `backend/.env`.

**בעברית:** אפשר להאזין מהטלפון — חבר את הטלפון לאותו Wi‑Fi, פתח את כתובת הרשת המקומית (למשל `http://192.168.x.x:5173`), והוסף את כתובת ה-redirect בהגדרות SoundCloud.

## Features

- Sign in with SoundCloud (OAuth 2.1 + PKCE)
- Browse your playlists
- Play full tracks with HLS streaming
- Shuffle, repeat, and queue controls
- No in-app advertisements or promotional banners
- Mobile-friendly layout — works on phone via local Wi‑Fi

## API endpoints

- `GET /api/auth/status` — configuration and auth state
- `GET /api/auth/login` — start OAuth flow
- `GET /api/auth/callback` — OAuth callback
- `POST /api/auth/logout` — sign out
- `GET /api/me` — authenticated user profile
- `GET /api/playlists` — your playlists
- `GET /api/playlists/{id}` — playlist with tracks
- `GET /api/tracks/{id}/stream` — stream URL for a track

## Tests

```bash
cd backend && source .venv/bin/activate && pytest
```

## Notes

- Tracks marked as **preview** by SoundCloud will only play a short clip (this is a platform restriction, not an ad).
- Some tracks may be blocked from off-platform streaming by the uploader or SoundCloud.
- Respect SoundCloud's [Terms of Use](https://soundcloud.com/terms-of-use) and attribution requirements when sharing streams.
