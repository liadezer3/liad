import type { PlaylistSummary } from '../types'

interface Props {
  playlists: PlaylistSummary[]
  activeId: number | null
  loading: boolean
  onSelect: (id: number) => void
}

export default function PlaylistSidebar({ playlists, activeId, loading, onSelect }: Props) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Playlists</h2>
      </div>
      <div className="playlist-list">
        {loading && <p className="muted">Loading playlists…</p>}
        {!loading && playlists.length === 0 && <p className="muted">No playlists found.</p>}
        {playlists.map((playlist) => (
          <button
            key={playlist.id}
            type="button"
            className={`playlist-item ${activeId === playlist.id ? 'active' : ''}`}
            onClick={() => onSelect(playlist.id)}
          >
            <img
              src={playlist.artwork_url || '/favicon.svg'}
              alt=""
              className="playlist-thumb"
            />
            <div className="playlist-meta">
              <span className="playlist-title">{playlist.title}</span>
              <span className="playlist-count">{playlist.track_count} tracks</span>
            </div>
          </button>
        ))}
      </div>
    </aside>
  )
}
