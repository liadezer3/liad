import { useCallback, useEffect, useRef, useState } from 'react'
import Hls from 'hls.js'
import { api } from '../api/client'
import type { Track } from '../types'

function formatTime(ms: number) {
  const total = Math.floor(ms / 1000)
  const m = Math.floor(total / 60)
  const s = total % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

export function usePlayer() {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const hlsRef = useRef<Hls | null>(null)
  const [queue, setQueue] = useState<Track[]>([])
  const [index, setIndex] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [duration, setDuration] = useState(0)
  const [shuffle, setShuffle] = useState(false)
  const [repeat, setRepeat] = useState<'off' | 'all' | 'one'>('off')
  const [error, setError] = useState<string | null>(null)
  const [isPreview, setIsPreview] = useState(false)

  const current = queue[index] ?? null

  const destroyHls = useCallback(() => {
    hlsRef.current?.destroy()
    hlsRef.current = null
  }, [])

  const playTrackAt = useCallback(
    async (tracks: Track[], startIndex: number) => {
      setQueue(tracks)
      setIndex(startIndex)
      setError(null)
    },
    [],
  )

  const loadAndPlay = useCallback(
    async (track: Track) => {
      const audio = audioRef.current
      if (!audio) return

      setLoading(true)
      setError(null)
      destroyHls()

      try {
        const { stream_url, is_preview } = await api.stream(track.id)
        setIsPreview(is_preview)

        if (stream_url.includes('.m3u8')) {
          if (Hls.isSupported()) {
            const hls = new Hls()
            hlsRef.current = hls
            hls.loadSource(stream_url)
            hls.attachMedia(audio)
            await new Promise<void>((resolve, reject) => {
              hls.on(Hls.Events.MANIFEST_PARSED, () => resolve())
              hls.on(Hls.Events.ERROR, (_, data) => {
                if (data.fatal) reject(new Error('Failed to load stream'))
              })
            })
          } else if (audio.canPlayType('application/vnd.apple.mpegurl')) {
            audio.src = stream_url
          } else {
            throw new Error('HLS playback is not supported in this browser')
          }
        } else {
          audio.src = stream_url
        }

        await audio.play()
        setPlaying(true)
      } catch (err) {
        setPlaying(false)
        setError(err instanceof Error ? err.message : 'Playback failed')
      } finally {
        setLoading(false)
      }
    },
    [destroyHls],
  )

  useEffect(() => {
    if (!current) return
    void loadAndPlay(current)
    return () => destroyHls()
  }, [current?.id, loadAndPlay, destroyHls])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const onTime = () => {
      setProgress(audio.currentTime * 1000)
      setDuration((audio.duration || 0) * 1000)
    }
    const onEnded = () => {
      if (repeat === 'one') {
        audio.currentTime = 0
        void audio.play()
        return
      }
      if (index < queue.length - 1) {
        setIndex((i) => i + 1)
      } else if (repeat === 'all' && queue.length > 0) {
        setIndex(0)
      } else {
        setPlaying(false)
      }
    }

    audio.addEventListener('timeupdate', onTime)
    audio.addEventListener('loadedmetadata', onTime)
    audio.addEventListener('ended', onEnded)
    return () => {
      audio.removeEventListener('timeupdate', onTime)
      audio.removeEventListener('loadedmetadata', onTime)
      audio.removeEventListener('ended', onEnded)
    }
  }, [index, queue.length, repeat])

  const togglePlay = useCallback(async () => {
    const audio = audioRef.current
    if (!audio || !current) return
    if (playing) {
      audio.pause()
      setPlaying(false)
    } else {
      await audio.play()
      setPlaying(true)
    }
  }, [current, playing])

  const next = useCallback(() => {
    if (queue.length === 0) return
    if (shuffle) {
      const nextIndex = Math.floor(Math.random() * queue.length)
      setIndex(nextIndex)
      return
    }
    setIndex((i) => (i + 1) % queue.length)
  }, [queue.length, shuffle])

  const prev = useCallback(() => {
    const audio = audioRef.current
    if (audio && audio.currentTime > 3) {
      audio.currentTime = 0
      return
    }
    if (queue.length === 0) return
    setIndex((i) => (i - 1 + queue.length) % queue.length)
  }, [queue.length])

  const seek = useCallback((ms: number) => {
    const audio = audioRef.current
    if (!audio) return
    audio.currentTime = ms / 1000
    setProgress(ms)
  }, [])

  const cycleRepeat = useCallback(() => {
    setRepeat((r) => (r === 'off' ? 'all' : r === 'all' ? 'one' : 'off'))
  }, [])

  return {
    audioRef,
    current,
    queue,
    index,
    playing,
    loading,
    progress,
    duration,
    shuffle,
    repeat,
    error,
    isPreview,
    formatTime,
    playTrackAt,
    togglePlay,
    next,
    prev,
    seek,
    setShuffle,
    cycleRepeat,
    playIndex: setIndex,
  }
}
