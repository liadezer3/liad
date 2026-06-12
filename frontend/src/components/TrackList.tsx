import type { PlaylistDetail, Track } from '../types'

interface Props {
  playlist: PlaylistDetail | null
  loading: boolean
  currentTrackId: number | null
  onPlay: (tracks: Track[], index: number) => void
}

function formatDuration(ms: number) {
  const total = Math.floor(ms / 1000)
  const m = Math.floor(total / 60)
  const s = total % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

export default function TrackList({ playlist, loading, currentTrackId, onPlay }: Props) {
  if (loading) {
    return <div className="track-area"><p className="muted">Loading tracks…</p></div>
  }

  if (!playlist) {
    return (
      <div className="track-area empty-state">
        <h2>Select a playlist</h2>
        <p>Choose a playlist from the sidebar to start listening.</p>
      </div>
    )
  }

  return (
    <div className="track-area">
      <header className="playlist-hero">
        <img
          src={playlist.artwork_url || '/favicon.svg'}
          alt=""
          className="playlist-hero-art"
        />
        <div>
          <p className="eyebrow">Playlist</p>
          <h1>{playlist.title}</h1>
          {playlist.description && <p className="playlist-desc">{playlist.description}</p>}
          <p className="playlist-meta-line">{playlist.tracks.length} tracks</p>
        </div>
      </header>

      <div className="track-table">
        <div className="track-row track-header">
          <span>#</span>
          <span>Title</span>
          <span>Artist</span>
          <span>Duration</span>
        </div>
        {playlist.tracks.map((track, i) => (
          <button
            key={track.id}
            type="button"
            className={`track-row ${currentTrackId === track.id ? 'playing' : ''}`}
            onClick={() => onPlay(playlist.tracks, i)}
          >
            <span>{i + 1}</span>
            <span className="track-title-cell">
              <img src={track.artwork_url || '/favicon.svg'} alt="" />
              <span>{track.title}</span>
              {track.access === 'preview' && <span className="badge">Preview</span>}
            </span>
            <span>{track.artist}</span>
            <span>{formatDuration(track.duration_ms)}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
