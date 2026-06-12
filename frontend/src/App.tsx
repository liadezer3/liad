import { useCallback, useEffect, useState } from 'react'
import { api } from './api/client'
import LoginScreen from './components/LoginScreen'
import PlayerBar from './components/PlayerBar'
import PlaylistSidebar from './components/PlaylistSidebar'
import TrackList from './components/TrackList'
import { usePlayer } from './hooks/usePlayer'
import type { PlaylistDetail, PlaylistSummary, UserProfile } from './types'
import './App.css'

export default function App() {
  const [auth, setAuth] = useState<{ configured: boolean; authenticated: boolean } | null>(null)
  const [user, setUser] = useState<UserProfile | null>(null)
  const [playlists, setPlaylists] = useState<PlaylistSummary[]>([])
  const [activePlaylistId, setActivePlaylistId] = useState<number | null>(null)
  const [playlistDetail, setPlaylistDetail] = useState<PlaylistDetail | null>(null)
  const [loadingPlaylists, setLoadingPlaylists] = useState(false)
  const [loadingTracks, setLoadingTracks] = useState(false)

  const player = usePlayer()

  const loadSession = useCallback(async () => {
    const status = await api.authStatus()
    setAuth(status)
    if (!status.authenticated) {
      setUser(null)
      setPlaylists([])
      return
    }
    setLoadingPlaylists(true)
    try {
      const [profile, list] = await Promise.all([api.me(), api.playlists()])
      setUser(profile)
      setPlaylists(list)
      if (list.length > 0) {
        setActivePlaylistId((current) => current ?? list[0].id)
      }
    } finally {
      setLoadingPlaylists(false)
    }
  }, [])

  useEffect(() => {
    void loadSession().catch(() => setAuth({ configured: false, authenticated: false }))
  }, [loadSession])

  useEffect(() => {
    if (!activePlaylistId || !auth?.authenticated) return
    setLoadingTracks(true)
    api
      .playlist(activePlaylistId)
      .then(setPlaylistDetail)
      .catch(() => setPlaylistDetail(null))
      .finally(() => setLoadingTracks(false))
  }, [activePlaylistId, auth?.authenticated])

  const handleLogout = async () => {
    await api.logout()
    setAuth({ configured: auth?.configured ?? true, authenticated: false })
    setUser(null)
    setPlaylists([])
    setPlaylistDetail(null)
    setActivePlaylistId(null)
  }

  if (!auth) {
    return <div className="app-shell loading-shell">Loading…</div>
  }

  if (!auth.authenticated) {
    return (
      <div className="app-shell">
        <LoginScreen configured={auth.configured} />
      </div>
    )
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">Wavebox</div>
        <div className="topbar-user">
          <img src={user?.avatar_url || '/favicon.svg'} alt="" />
          <span>{user?.full_name}</span>
          <button type="button" onClick={() => void handleLogout()}>
            Sign out
          </button>
        </div>
      </header>

      <main className="main-layout">
        <PlaylistSidebar
          playlists={playlists}
          activeId={activePlaylistId}
          loading={loadingPlaylists}
          onSelect={setActivePlaylistId}
        />
        <TrackList
          playlist={playlistDetail}
          loading={loadingTracks}
          currentTrackId={player.current?.id ?? null}
          onPlay={player.playTrackAt}
        />
      </main>

      <PlayerBar
        track={player.current}
        playing={player.playing}
        loading={player.loading}
        progress={player.progress}
        duration={player.duration}
        shuffle={player.shuffle}
        repeat={player.repeat}
        isPreview={player.isPreview}
        error={player.error}
        formatTime={player.formatTime}
        onToggle={() => void player.togglePlay()}
        onPrev={player.prev}
        onNext={player.next}
        onSeek={player.seek}
        onToggleShuffle={() => player.setShuffle((s) => !s)}
        onCycleRepeat={player.cycleRepeat}
      />

      <audio ref={player.audioRef} preload="auto" />
    </div>
  )
}
