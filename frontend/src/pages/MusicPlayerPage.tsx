import { useEffect, useRef, useState } from 'react'
import {
  loadWidgetApi,
  widgetIframeSrc,
  type ScPlayProgress,
  type ScSound,
  type ScWidget,
} from '../lib/soundcloudWidget'
import './MusicPlayerPage.css'

const STORAGE_KEY = 'soundcloud-player-url'
const EXAMPLE_URL = 'https://soundcloud.com/forss/sets/soulhack'

type Status = 'idle' | 'loading' | 'ready' | 'error'

function formatMs(ms: number): string {
  const totalSeconds = Math.max(0, Math.floor(ms / 1000))
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${minutes}:${String(seconds).padStart(2, '0')}`
}

function artworkUrl(sound: ScSound | undefined): string | null {
  const raw = sound?.artwork_url ?? sound?.user?.avatar_url ?? null
  return raw ? raw.replace('-large', '-t500x500') : null
}

function normalizeUrl(input: string): string | null {
  let url = input.trim()
  if (!url) return null
  if (!/^https?:\/\//i.test(url)) url = `https://${url}`
  try {
    const { hostname } = new URL(url)
    if (!/(^|\.)soundcloud\.com$/i.test(hostname)) return null
  } catch {
    return null
  }
  return url
}

const PrevIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M6 5h2v14H6zM20 5v14l-10-7z" fill="currentColor" />
  </svg>
)
const NextIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M16 5h2v14h-2zM4 5l10 7-10 7z" fill="currentColor" />
  </svg>
)
const PlayIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M7 4.5l13 7.5-13 7.5z" fill="currentColor" />
  </svg>
)
const PauseIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M6 4h4v16H6zM14 4h4v16h-4z" fill="currentColor" />
  </svg>
)
const NoteIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path
      d="M9 18.5a3 3 0 1 1-2-2.83V6l12-2.5v11a3 3 0 1 1-2-2.83V7L9 8.9z"
      fill="currentColor"
    />
  </svg>
)
const VolumeIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path
      d="M4 9v6h4l5 4V5L8 9zM16.5 12a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zM14 3.8v2.1a6.5 6.5 0 0 1 0 12.2v2.1a8.5 8.5 0 0 0 0-16.4z"
      fill="currentColor"
    />
  </svg>
)

export default function MusicPlayerPage() {
  const [inputUrl, setInputUrl] = useState(
    () => localStorage.getItem(STORAGE_KEY) ?? '',
  )
  const [loadedUrl, setLoadedUrl] = useState(
    () => localStorage.getItem(STORAGE_KEY) ?? '',
  )
  const [status, setStatus] = useState<Status>(loadedUrl ? 'loading' : 'idle')
  const [error, setError] = useState<string | null>(null)
  const [tracks, setTracks] = useState<ScSound[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [positionMs, setPositionMs] = useState(0)
  const [durationMs, setDurationMs] = useState(0)
  const [volume, setVolume] = useState(80)

  const iframeRef = useRef<HTMLIFrameElement | null>(null)
  const widgetRef = useRef<ScWidget | null>(null)
  const seekingRef = useRef(false)
  const volumeRef = useRef(volume)

  useEffect(() => {
    if (!loadedUrl) return
    let cancelled = false
    let widget: ScWidget | null = null
    let boundEvents: string[] = []

    loadWidgetApi()
      .then((SC) => {
        if (cancelled || !iframeRef.current) return
        widget = SC.Widget(iframeRef.current)
        widgetRef.current = widget
        const Events = SC.Widget.Events

        const refreshSounds = () => {
          widget?.getSounds((sounds) => {
            if (!cancelled) setTracks(sounds ?? [])
          })
        }
        const refreshCurrent = () => {
          widget?.getCurrentSoundIndex((index) => {
            if (!cancelled) setCurrentIndex(index ?? 0)
          })
          widget?.getCurrentSound((sound) => {
            if (cancelled || !sound) return
            setDurationMs(sound.duration ?? 0)
            setTracks((prev) =>
              prev.map((t) => (t.id === sound.id ? { ...t, ...sound } : t)),
            )
          })
        }

        const bind = (event: string, handler: (data?: unknown) => void) => {
          widget?.bind(event, handler)
          boundEvents.push(event)
        }

        bind(Events.READY, () => {
          if (cancelled) return
          setStatus('ready')
          widget?.setVolume(volumeRef.current)
          refreshSounds()
          refreshCurrent()
        })
        bind(Events.PLAY, () => {
          if (cancelled) return
          setIsPlaying(true)
          refreshCurrent()
          refreshSounds()
        })
        bind(Events.PAUSE, () => {
          if (!cancelled) setIsPlaying(false)
        })
        bind(Events.FINISH, () => {
          if (!cancelled) setIsPlaying(false)
        })
        bind(Events.PLAY_PROGRESS, (data) => {
          if (cancelled || seekingRef.current) return
          const progress = data as ScPlayProgress | undefined
          setPositionMs(progress?.currentPosition ?? 0)
        })
        bind(Events.ERROR, () => {
          if (cancelled) return
          setStatus('error')
          setError(
            'SoundCloud could not load this URL. Make sure it points to a public playlist, album, or track.',
          )
        })
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setStatus('error')
          setError(err.message)
        }
      })

    return () => {
      cancelled = true
      boundEvents.forEach((event) => widget?.unbind(event))
      boundEvents = []
      widgetRef.current = null
    }
  }, [loadedUrl])

  const handleLoad = (raw: string) => {
    const url = normalizeUrl(raw)
    if (!url) {
      setError('Enter a soundcloud.com link, e.g. https://soundcloud.com/artist/sets/my-playlist')
      setStatus(loadedUrl ? status : 'idle')
      return
    }
    localStorage.setItem(STORAGE_KEY, url)
    setInputUrl(url)
    setError(null)
    if (url === loadedUrl) return
    setStatus('loading')
    setTracks([])
    setCurrentIndex(0)
    setIsPlaying(false)
    setPositionMs(0)
    setDurationMs(0)
    setLoadedUrl(url)
  }

  const commitSeek = (value: number) => {
    seekingRef.current = false
    widgetRef.current?.seekTo(value)
  }

  const handleVolume = (value: number) => {
    setVolume(value)
    volumeRef.current = value
    widgetRef.current?.setVolume(value)
  }

  const currentSound = tracks[currentIndex]
  const artwork = artworkUrl(currentSound)
  const ready = status === 'ready'

  return (
    <div className="page music-page">
      <header className="page-header">
        <h1>Music Player</h1>
        <p>
          Paste a SoundCloud playlist link and listen in a clean, ad-free
          interface — no banners, no pop-ups, no interruptions from this app.
        </p>
      </header>

      <form
        className="card url-form"
        onSubmit={(e) => {
          e.preventDefault()
          handleLoad(inputUrl)
        }}
      >
        <input
          type="text"
          value={inputUrl}
          onChange={(e) => setInputUrl(e.target.value)}
          placeholder="https://soundcloud.com/artist/sets/my-playlist"
          aria-label="SoundCloud playlist URL"
        />
        <button type="submit" className="btn-load">
          Load playlist
        </button>
        <button
          type="button"
          className="btn-demo"
          onClick={() => handleLoad(EXAMPLE_URL)}
        >
          Try a demo playlist
        </button>
      </form>

      {error && <div className="error-banner">{error}</div>}

      {status === 'idle' && !error && (
        <div className="card empty-state">
          <NoteIcon />
          <h2>No playlist loaded yet</h2>
          <p>
            Open your playlist on soundcloud.com, copy the link from the
            address bar, and paste it in the field. Likes, albums, and single
            tracks work too.
          </p>
        </div>
      )}

      {status === 'loading' && (
        <div className="card empty-state">
          <div className="spinner" aria-hidden="true" />
          <p>Connecting to SoundCloud…</p>
        </div>
      )}

      {ready && (
        <div className="player-grid">
          <section className="card now-playing">
            {artwork ? (
              <img className="artwork" src={artwork} alt="Album artwork" />
            ) : (
              <div className="artwork artwork-placeholder">
                <NoteIcon />
              </div>
            )}
            <div className="track-meta">
              <h2>{currentSound?.title ?? `Track ${currentIndex + 1}`}</h2>
              <p>{currentSound?.user?.username ?? 'Unknown artist'}</p>
            </div>

            <div className="seek-row">
              <span className="time">{formatMs(positionMs)}</span>
              <input
                type="range"
                min={0}
                max={Math.max(durationMs, 1)}
                value={Math.min(positionMs, durationMs || positionMs)}
                onChange={(e) => {
                  seekingRef.current = true
                  setPositionMs(Number(e.target.value))
                }}
                onPointerUp={(e) => commitSeek(Number(e.currentTarget.value))}
                onKeyUp={(e) => commitSeek(Number(e.currentTarget.value))}
                aria-label="Seek"
              />
              <span className="time">{formatMs(durationMs)}</span>
            </div>

            <div className="controls">
              <button
                type="button"
                className="ctrl"
                onClick={() => widgetRef.current?.prev()}
                aria-label="Previous track"
              >
                <PrevIcon />
              </button>
              <button
                type="button"
                className="ctrl ctrl-main"
                onClick={() => widgetRef.current?.toggle()}
                aria-label={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? <PauseIcon /> : <PlayIcon />}
              </button>
              <button
                type="button"
                className="ctrl"
                onClick={() => widgetRef.current?.next()}
                aria-label="Next track"
              >
                <NextIcon />
              </button>
            </div>

            <div className="volume-row">
              <VolumeIcon />
              <input
                type="range"
                min={0}
                max={100}
                value={volume}
                onChange={(e) => handleVolume(Number(e.target.value))}
                aria-label="Volume"
              />
            </div>

            {currentSound?.permalink_url && (
              <a
                className="sc-link"
                href={currentSound.permalink_url}
                target="_blank"
                rel="noreferrer"
              >
                Open on SoundCloud ↗
              </a>
            )}
          </section>

          <section className="card track-list">
            <h2>
              Playlist
              <span className="track-count">
                {tracks.length} track{tracks.length === 1 ? '' : 's'}
              </span>
            </h2>
            <ol>
              {tracks.map((track, i) => (
                <li key={track.id ?? i}>
                  <button
                    type="button"
                    className={i === currentIndex ? 'track active' : 'track'}
                    onClick={() => widgetRef.current?.skip(i)}
                  >
                    <span className="track-num">
                      {i === currentIndex && isPlaying ? (
                        <span className="eq" aria-hidden="true">
                          <i />
                          <i />
                          <i />
                        </span>
                      ) : (
                        i + 1
                      )}
                    </span>
                    <span className="track-title">
                      {track.title ?? `Track ${i + 1}`}
                      <small>{track.user?.username ?? ''}</small>
                    </span>
                    <span className="track-duration">
                      {track.duration ? formatMs(track.duration) : '–:––'}
                    </span>
                  </button>
                </li>
              ))}
            </ol>
          </section>
        </div>
      )}

      {loadedUrl && (
        <iframe
          key={loadedUrl}
          ref={iframeRef}
          className="sc-embed"
          src={widgetIframeSrc(loadedUrl)}
          title="SoundCloud player"
          allow="autoplay"
        />
      )}

      <p className="player-note">
        This interface is ad-free. Audio streams through SoundCloud&apos;s
        official embedded player, so artists still get their plays counted.
      </p>
    </div>
  )
}
