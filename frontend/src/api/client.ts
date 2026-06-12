import type {
  AuthStatus,
  NetworkInfo,
  PlaylistDetail,
  PlaylistSummary,
  StreamInfo,
  UserProfile,
} from '../types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    credentials: 'include',
    ...init,
    headers: {
      Accept: 'application/json',
      ...(init?.headers ?? {}),
    },
  })

  if (!response.ok) {
    let detail = response.statusText
    try {
      const body = await response.json()
      detail = body.detail ?? detail
    } catch {
      // ignore
    }
    throw new Error(detail)
  }

  return response.json() as Promise<T>
}

export const api = {
  networkInfo: () => request<NetworkInfo>('/api/network-info'),
  authStatus: () => request<AuthStatus>('/api/auth/status'),
  me: () => request<UserProfile>('/api/me'),
  playlists: () => request<PlaylistSummary[]>('/api/playlists'),
  playlist: (id: number) => request<PlaylistDetail>(`/api/playlists/${id}`),
  stream: (trackId: number) => request<StreamInfo>(`/api/tracks/${trackId}/stream`),
  logout: () => request<{ status: string }>('/api/auth/logout', { method: 'POST' }),
}

export function loginUrl() {
  return '/api/auth/login'
}
