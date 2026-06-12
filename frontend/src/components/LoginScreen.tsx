import { loginUrl } from '../api/client'

interface Props {
  configured: boolean
}

export default function LoginScreen({ configured }: Props) {
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
SOUNDCLOUD_REDIRECT_URI=http://127.0.0.1:8000/api/auth/callback`}</pre>
          </div>
        )}
      </div>
    </div>
  )
}
