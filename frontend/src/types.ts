export interface AuthStatus {
  configured: boolean
  authenticated: boolean
}

export interface NetworkInfo {
  lan_ip: string | null
  mobile_url: string | null
  redirect_uri_hint: string | null
}

export interface UserProfile {
  id: number
  username: string
  full_name: string
  avatar_url: string | null
  permalink_url: string
}

export interface PlaylistSummary {
  id: number
  title: string
  description: string | null
  artwork_url: string | null
  track_count: number
  permalink_url: string
}

export interface Track {
  id: number
  title: string
  artist: string
  duration_ms: number
  artwork_url: string | null
  permalink_url: string
  access: string
}

export interface PlaylistDetail {
  id: number
  title: string
  description: string | null
  artwork_url: string | null
  permalink_url: string
  tracks: Track[]
}

export interface StreamInfo {
  stream_url: string
  is_preview: boolean
}
