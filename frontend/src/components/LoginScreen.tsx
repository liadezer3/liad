import { useEffect, useState } from 'react'
import { api, loginUrl } from '../api/client'
import type { NetworkInfo } from '../types'

interface Props {
  configured: boolean
}

export default function LoginScreen({ configured }: Props) {
  const [network, setNetwork] = useState<NetworkInfo | null>(null)

  useEffect(() => {
    api.networkInfo().then(setNetwork).catch(() => setNetwork(null))
  }, [])

  return (
    <div className="login-screen">
      <div className="login-card">
        <div className="login-logo">Wavebox</div>
        <h1>Your playlists, uninterrupted</h1>
        <p>
          Stream your SoundCloud playlists in a clean, ad-free player. No banners, no interruptions —
          just music.
        </p>

        {configured ? (
          <a className="btn-primary" href={loginUrl()}>
            Connect SoundCloud
          </a>
        ) : (
          <div className="login-setup">
            <p className="setup-title">Setup required</p>
            <p>
              Register an app at{' '}
              <a href="https://soundcloud.com/you/apps" target="_blank" rel="noreferrer">
                soundcloud.com/you/apps
              </a>{' '}
              and add your credentials to <code>backend/.env</code>:
            </p>
            <pre>{`SOUNDCLOUD_CLIENT_ID=your_client_id
SOUNDCLOUD_CLIENT_SECRET=your_client_secret
SOUNDCLOUD_REDIRECT_URIS=http://127.0.0.1:5173/api/auth/callback,http://YOUR_LAN_IP:5173/api/auth/callback`}</pre>
          </div>
        )}

        {network?.mobile_url && (
          <div className="mobile-hint">
            <p className="setup-title">📱 Listen on your phone</p>
            <p>
              Make sure your phone is on the <strong>same Wi‑Fi</strong> as this computer, then open:
            </p>
            <a className="mobile-url" href={network.mobile_url}>
              {network.mobile_url}
            </a>
            <p className="mobile-note">
              Add this redirect URI in your SoundCloud app settings:
              <br />
              <code>{network.redirect_uri_hint}</code>
            </p>
            <p className="mobile-note hebrew">
              אפשר להאזין גם מהטלפון — חבר את הטלפון לאותו Wi‑Fi ופתח את הקישור למעלה.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
