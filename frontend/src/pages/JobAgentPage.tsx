import { useState } from 'react'
import type { FormEvent } from 'react'
import { scanJobs } from '../api/client'
import type { JobSearchResult } from '../types'
import './PageShared.css'
import './JobAgentPage.css'

type Coordinates = {
  latitude: number
  longitude: number
}

type LocationStatus = 'idle' | 'requesting' | 'granted' | 'denied' | 'unavailable'

const salaryFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})

function formatSalary(min: number | null, max: number | null) {
  if (min && max) return `${salaryFormatter.format(min)} - ${salaryFormatter.format(max)}`
  if (max) return `Up to ${salaryFormatter.format(max)}`
  if (min) return `From ${salaryFormatter.format(min)}`
  return 'Salary not listed'
}

function formatDistance(distance: number | null) {
  return distance == null ? null : `${distance.toFixed(1)} mi away`
}

export default function JobAgentPage() {
  const [query, setQuery] = useState('engineer')
  const [locationLabel, setLocationLabel] = useState('')
  const [radiusMiles, setRadiusMiles] = useState(50)
  const [includeRemote, setIncludeRemote] = useState(true)
  const [coords, setCoords] = useState<Coordinates | null>(null)
  const [locationStatus, setLocationStatus] = useState<LocationStatus>('idle')
  const [locationNotice, setLocationNotice] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<JobSearchResult | null>(null)

  function requestLocation(): Promise<Coordinates | null> {
    if (!navigator.geolocation) {
      setLocationStatus('unavailable')
      setLocationNotice('Location services are unavailable in this browser. Enter a city to scan nearby jobs.')
      return Promise.resolve(null)
    }

    setLocationStatus('requesting')
    setLocationNotice('Waiting for browser location permission...')

    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const nextCoords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          }
          setCoords(nextCoords)
          setLocationStatus('granted')
          setLocationNotice('Location permission granted. Scanning jobs near your current area.')
          resolve(nextCoords)
        },
        () => {
          setCoords(null)
          setLocationStatus('denied')
          setLocationNotice('Location permission was not granted. Scanning by typed city or all markets.')
          resolve(null)
        },
        { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 },
      )
    })
  }

  async function handleScan(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setLoading(true)
    setError(null)

    try {
      let activeCoords = coords
      if (!activeCoords && !locationLabel.trim()) {
        activeCoords = await requestLocation()
      }

      const data = await scanJobs({
        query,
        latitude: activeCoords?.latitude,
        longitude: activeCoords?.longitude,
        location_label: activeCoords ? 'Current location' : locationLabel.trim() || undefined,
        radius_miles: radiusMiles,
        include_remote: includeRemote,
      })
      setResult(data)
    } catch (e) {
      setResult(null)
      setError(e instanceof Error ? e.message : 'Job scan failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page job-agent-page">
      <header className="page-header">
        <p className="eyebrow">Location-aware agent</p>
        <h1>Job Scanner Agent</h1>
        <p>
          Ask for location permission, scan configured job sources, and organize jobs by salary,
          title, location, and rating.
        </p>
      </header>

      <section className="card scanner-card">
        <form className="job-search-form" onSubmit={handleScan}>
          <label>
            Job title or keyword
            <input value={query} onChange={(event) => setQuery(event.target.value)} required />
          </label>
          <label>
            City or area fallback
            <input
              value={locationLabel}
              onChange={(event) => setLocationLabel(event.target.value)}
              placeholder="New York, NY"
            />
          </label>
          <label>
            Radius in miles
            <input
              type="number"
              min={5}
              max={250}
              value={radiusMiles}
              onChange={(event) => setRadiusMiles(Number(event.target.value))}
            />
          </label>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={includeRemote}
              onChange={(event) => setIncludeRemote(event.target.checked)}
            />
            Include remote jobs
          </label>
          <div className="form-actions">
            <button type="button" className="btn secondary" onClick={requestLocation}>
              {locationStatus === 'requesting' ? 'Requesting location...' : 'Use my current location'}
            </button>
            <button type="submit" className="btn primary" disabled={loading || locationStatus === 'requesting'}>
              {loading ? 'Scanning jobs...' : 'Scan jobs'}
            </button>
          </div>
        </form>
        {locationNotice && <p className={`location-note ${locationStatus}`}>{locationNotice}</p>}
      </section>

      {error && <p className="error-banner">{error}</p>}

      {result && (
        <section className="job-results">
          <div className="results-summary card">
            <div>
              <h2>{result.total_results} jobs found</h2>
              <p>
                Query: <strong>{result.query}</strong> near <strong>{result.location_label}</strong>
              </p>
            </div>
            <div className="source-list">
              {result.sources_scanned.map((source) => (
                <span key={source}>{source}</span>
              ))}
            </div>
          </div>

          {result.groups.length === 0 ? (
            <div className="card empty-state">
              <h2>No matching jobs yet</h2>
              <p>Try a broader title, larger radius, or enable remote jobs.</p>
            </div>
          ) : (
            result.groups.map((group) => (
              <article className="job-group card" key={`${group.title}-${group.location}`}>
                <div className="group-header">
                  <div>
                    <h2>{group.title}</h2>
                    <p>{group.location}</p>
                  </div>
                  <div className="group-score">
                    <span>{group.average_rating.toFixed(1)}</span>
                    <small>avg rating</small>
                  </div>
                </div>
                <div className="job-list">
                  {group.jobs.map((job) => (
                    <div className="job-card" key={job.id}>
                      <div>
                        <h3>{job.company}</h3>
                        <p>{job.summary}</p>
                        <div className="job-meta">
                          <span>{formatSalary(job.salary_min, job.salary_max)}</span>
                          <span>{job.rating.toFixed(1)} rating</span>
                          <span>{job.job_type}</span>
                          {formatDistance(job.distance_miles) && <span>{formatDistance(job.distance_miles)}</span>}
                        </div>
                      </div>
                      <a href={job.source_url} target="_blank" rel="noreferrer">
                        Open on {job.source}
                      </a>
                    </div>
                  ))}
                </div>
              </article>
            ))
          )}
        </section>
      )}
    </div>
  )
}
