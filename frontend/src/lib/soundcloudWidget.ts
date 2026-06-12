// Thin loader + typings for the official SoundCloud Widget API.
// Docs: https://developers.soundcloud.com/docs/api/html5-widget

export interface ScSound {
  id: number
  title?: string
  duration?: number
  artwork_url?: string | null
  permalink_url?: string
  user?: {
    username?: string
    avatar_url?: string
  }
}

export interface ScPlayProgress {
  currentPosition: number
  relativePosition: number
  loadedProgress: number
}

export interface ScWidget {
  bind(event: string, callback: (data?: unknown) => void): void
  unbind(event: string): void
  load(url: string, options?: Record<string, unknown>): void
  play(): void
  pause(): void
  toggle(): void
  seekTo(milliseconds: number): void
  setVolume(volume: number): void
  next(): void
  prev(): void
  skip(index: number): void
  getSounds(callback: (sounds: ScSound[]) => void): void
  getCurrentSound(callback: (sound: ScSound | undefined) => void): void
  getCurrentSoundIndex(callback: (index: number) => void): void
  getDuration(callback: (milliseconds: number) => void): void
  getPosition(callback: (milliseconds: number) => void): void
  isPaused(callback: (paused: boolean) => void): void
}

export interface ScNamespace {
  Widget: {
    (element: HTMLIFrameElement | string): ScWidget
    Events: {
      READY: string
      PLAY: string
      PAUSE: string
      FINISH: string
      PLAY_PROGRESS: string
      ERROR: string
      SEEK: string
      LOAD_PROGRESS: string
    }
  }
}

declare global {
  interface Window {
    SC?: ScNamespace
  }
}

const WIDGET_API_SRC = 'https://w.soundcloud.com/player/api.js'

let loadPromise: Promise<ScNamespace> | null = null

export function loadWidgetApi(): Promise<ScNamespace> {
  if (window.SC?.Widget) return Promise.resolve(window.SC)
  if (!loadPromise) {
    loadPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = WIDGET_API_SRC
      script.async = true
      script.onload = () => {
        if (window.SC?.Widget) {
          resolve(window.SC)
        } else {
          loadPromise = null
          reject(new Error('SoundCloud player failed to initialise.'))
        }
      }
      script.onerror = () => {
        loadPromise = null
        reject(new Error('Could not reach SoundCloud. Check your connection and retry.'))
      }
      document.head.appendChild(script)
    })
  }
  return loadPromise
}

export function widgetIframeSrc(soundcloudUrl: string): string {
  const params = new URLSearchParams({
    url: soundcloudUrl,
    auto_play: 'false',
    visual: 'false',
    show_artwork: 'true',
    show_comments: 'false',
    show_teaser: 'false',
    hide_related: 'true',
  })
  return `https://w.soundcloud.com/player/?${params.toString()}`
}
