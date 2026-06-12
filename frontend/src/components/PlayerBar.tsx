import type { Track } from '../types'

interface Props {
  track: Track | null
  playing: boolean
  loading: boolean
  progress: number
  duration: number
  shuffle: boolean
  repeat: 'off' | 'all' | 'one'
  isPreview: boolean
  error: string | null
  formatTime: (ms: number) => string
  onToggle: () => void
  onPrev: () => void
  onNext: () => void
  onSeek: (ms: number) => void
  onToggleShuffle: () => void
  onCycleRepeat: () => void
}

export default function PlayerBar({
  track,
  playing,
  loading,
  progress,
  duration,
  shuffle,
  repeat,
  isPreview,
  error,
  formatTime,
  onToggle,
  onPrev,
  onNext,
  onSeek,
  onToggleShuffle,
  onCycleRepeat,
}: Props) {
  if (!track) return null

  const pct = duration > 0 ? (progress / duration) * 100 : 0

  return (
    <footer className="player-bar">
      <div className="player-track">
        <img src={track.artwork_url || '/favicon.svg'} alt="" />
        <div>
          <div className="player-title">{track.title}</div>
          <div className="player-artist">{track.artist}</div>
        </div>
        {isPreview && <span className="badge">Preview</span>}
      </div>

      <div className="player-controls">
        <div className="control-buttons">
          <button type="button" className={shuffle ? 'active' : ''} onClick={onToggleShuffle} aria-label="Shuffle">
            ⇄
          </button>
          <button type="button" onClick={onPrev} aria-label="Previous">
            ⏮
          </button>
          <button type="button" className="play-btn" onClick={onToggle} disabled={loading} aria-label={playing ? 'Pause' : 'Play'}>
            {loading ? '…' : playing ? '⏸' : '▶'}
          </button>
          <button type="button" onClick={onNext} aria-label="Next">
            ⏭
          </button>
          <button
            type="button"
            className={repeat !== 'off' ? 'active' : ''}
            onClick={onCycleRepeat}
            aria-label="Repeat"
          >
            {repeat === 'one' ? '🔂' : '🔁'}
          </button>
        </div>

        <div className="progress-row">
          <span>{formatTime(progress)}</span>
          <input
            type="range"
            min={0}
            max={duration || 1}
            value={progress}
            onChange={(e) => onSeek(Number(e.target.value))}
          />
          <span>{formatTime(duration)}</span>
        </div>
        {error && <p className="player-error">{error}</p>}
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>

      <div className="player-attribution">
        <a href={track.permalink_url} target="_blank" rel="noreferrer">
          View on SoundCloud
        </a>
      </div>
    </footer>
  )
}
