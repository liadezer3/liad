from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
import html
import re
from typing import Any, Callable

import httpx

from app.schemas import JobGroup, JobListing, JobSearchRequest, JobSearchResult


SOURCES = [
    "Remotive",
    "Arbeitnow",
    "RemoteOK",
]

HTTP_HEADERS = {"User-Agent": "JobScannerAgent/1.0 (+https://example.local)"}
MAX_RESULTS_PER_SOURCE = 50
MAX_JOB_AGE_DAYS = 120


@dataclass(frozen=True)
class RawJob:
    id: str
    title: str
    company: str
    location: str
    source: str
    source_url: str
    salary_min: int | None
    salary_max: int | None
    rating: float
    job_type: str
    remote: bool
    posted_at: str
    summary: str
    description: str


Provider = Callable[[httpx.Client, str], list[RawJob]]
PROVIDERS: list[Provider] = []


def scan_jobs(body: JobSearchRequest) -> JobSearchResult:
    query = body.query.strip()
    location_label = _clean_location_label(body)
    raw_jobs = _fetch_live_jobs(query)
    listings = [_to_listing(job) for job in raw_jobs if _matches(job, body, query)]
    listings.sort(key=_job_sort_key)
    groups = _group_jobs(listings)

    return JobSearchResult(
        query=query,
        location_label=location_label,
        sources_scanned=SOURCES,
        total_results=len(listings),
        groups=groups,
    )


def _fetch_live_jobs(query: str) -> list[RawJob]:
    jobs: list[RawJob] = []
    with httpx.Client(headers=HTTP_HEADERS, timeout=15, follow_redirects=True) as client:
        for provider in PROVIDERS:
            try:
                jobs.extend(provider(client, query))
            except httpx.HTTPError:
                continue
    return _dedupe_jobs(jobs)


def _fetch_remotive(client: httpx.Client, query: str) -> list[RawJob]:
    response = client.get(
        "https://remotive.com/api/remote-jobs",
        params={"search": query, "limit": MAX_RESULTS_PER_SOURCE},
    )
    response.raise_for_status()
    jobs = response.json().get("jobs", [])

    results = []
    for item in jobs:
        description = _clean_text(item.get("description", ""))
        salary_min, salary_max = _parse_salary_range(item.get("salary", ""))
        posted_at = _parse_iso_date(item.get("publication_date"))
        results.append(
            RawJob(
                id=f"remotive-{item.get('id')}",
                title=_clean_text(item.get("title") or "Untitled role"),
                company=_clean_text(item.get("company_name") or "Unknown company"),
                location=_clean_text(item.get("candidate_required_location") or "Remote"),
                source="Remotive",
                source_url=item.get("url") or "https://remotive.com/remote-jobs",
                salary_min=salary_min,
                salary_max=salary_max,
                rating=_rate_job(salary_min, salary_max, posted_at, True, bool(description)),
                job_type=_clean_text(item.get("job_type") or "Remote"),
                remote=True,
                posted_at=posted_at,
                summary=_summarize(description),
                description=description,
            )
        )
    return results


def _fetch_arbeitnow(client: httpx.Client, query: str) -> list[RawJob]:
    response = client.get("https://www.arbeitnow.com/api/job-board-api")
    response.raise_for_status()
    jobs = response.json().get("data", [])[:MAX_RESULTS_PER_SOURCE]

    results = []
    for item in jobs:
        description = _clean_text(item.get("description", ""))
        salary_min, salary_max = _parse_salary_range(description)
        posted_at = _parse_unix_date(item.get("created_at"))
        job_types = item.get("job_types") or []
        remote = bool(item.get("remote"))
        results.append(
            RawJob(
                id=f"arbeitnow-{item.get('slug')}",
                title=_clean_text(item.get("title") or "Untitled role"),
                company=_clean_text(item.get("company_name") or "Unknown company"),
                location=_clean_text(item.get("location") or ("Remote" if remote else "Not listed")),
                source="Arbeitnow",
                source_url=item.get("url") or "https://www.arbeitnow.com/jobs",
                salary_min=salary_min,
                salary_max=salary_max,
                rating=_rate_job(salary_min, salary_max, posted_at, remote, bool(description)),
                job_type=", ".join(job_types) if job_types else ("Remote" if remote else "Full-time"),
                remote=remote,
                posted_at=posted_at,
                summary=_summarize(description),
                description=description,
            )
        )
    return results


def _fetch_remoteok(client: httpx.Client, query: str) -> list[RawJob]:
    response = client.get("https://remoteok.com/api")
    response.raise_for_status()
    payload = response.json()
    jobs = [item for item in payload if isinstance(item, dict) and item.get("id")][:MAX_RESULTS_PER_SOURCE]

    results = []
    for item in jobs:
        description = _clean_text(item.get("description") or item.get("company_logo") or "")
        salary_min = _safe_int(item.get("salary_min"))
        salary_max = _safe_int(item.get("salary_max"))
        posted_at = _parse_iso_date(item.get("date"))
        results.append(
            RawJob(
                id=f"remoteok-{item.get('id')}",
                title=_clean_text(item.get("position") or "Untitled role"),
                company=_clean_text(item.get("company") or "Unknown company"),
                location=_clean_text(item.get("location") or "Remote"),
                source="RemoteOK",
                source_url=item.get("url") or "https://remoteok.com",
                salary_min=salary_min,
                salary_max=salary_max,
                rating=_rate_job(salary_min, salary_max, posted_at, True, bool(description)),
                job_type="Remote",
                remote=True,
                posted_at=posted_at,
                summary=_summarize(description or "Remote role listed on RemoteOK."),
                description=description or "Open the source link to view the full RemoteOK description.",
            )
        )
    return results


def _matches(job: RawJob, body: JobSearchRequest, query: str) -> bool:
    if _days_old(job.posted_at) > MAX_JOB_AGE_DAYS:
        return False
    if not _matches_query(job, query):
        return False
    if job.remote and body.include_remote:
        return True
    if body.location_label:
        return _matches_location_label(job.location, body.location_label)
    return True


def _matches_query(job: RawJob, query: str) -> bool:
    terms = [term for term in query.lower().replace(",", " ").split() if term]
    if not terms:
        return True
    haystack = f"{job.title} {job.company} {job.summary} {job.description}".lower()
    return all(term in haystack for term in terms)


def _matches_location_label(job_location: str, label: str) -> bool:
    label_terms = {term for term in label.lower().replace(",", " ").split() if len(term) > 1}
    job_terms = {term for term in job_location.lower().replace(",", " ").split() if len(term) > 1}
    return bool(label_terms & job_terms)


def _clean_location_label(body: JobSearchRequest) -> str:
    if body.location_label and body.location_label.strip():
        return body.location_label.strip()
    if body.latitude is not None and body.longitude is not None:
        return "Current location"
    return "All configured markets"


def _to_listing(job: RawJob) -> JobListing:
    return JobListing(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        source=job.source,
        source_url=job.source_url,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        rating=job.rating,
        job_type=job.job_type,
        remote=job.remote,
        distance_miles=None,
        posted_at=job.posted_at,
        summary=job.summary,
        description=job.description,
    )


def _group_jobs(listings: list[JobListing]) -> list[JobGroup]:
    grouped: dict[tuple[str, str], list[JobListing]] = {}
    for listing in listings:
        grouped.setdefault((listing.title, listing.location), []).append(listing)

    groups = []
    for (title, location), jobs in grouped.items():
        jobs.sort(key=_job_sort_key)
        highest_salary = max((job.salary_max or job.salary_min or 0 for job in jobs), default=0) or None
        average_rating = round(sum(job.rating for job in jobs) / len(jobs), 1)
        groups.append(
            JobGroup(
                title=title,
                location=location,
                average_rating=average_rating,
                highest_salary=highest_salary,
                jobs=jobs,
            )
        )
    groups.sort(key=lambda group: (-(group.highest_salary or 0), -group.average_rating, group.title, group.location))
    return groups


def _job_sort_key(job: JobListing) -> tuple[int, int, float, str]:
    return (-(job.salary_max or 0), -(job.salary_min or 0), -job.rating, job.title)


def _dedupe_jobs(jobs: list[RawJob]) -> list[RawJob]:
    seen: set[tuple[str, str, str]] = set()
    unique = []
    for job in jobs:
        key = (job.title.lower(), job.company.lower(), job.source_url)
        if key in seen:
            continue
        seen.add(key)
        unique.append(job)
    return unique


def _clean_text(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _summarize(description: str) -> str:
    text = _clean_text(description)
    if len(text) <= 220:
        return text or "Open the source link to view the full posting details."
    return f"{text[:217].rstrip()}..."


def _parse_salary_range(text: Any) -> tuple[int | None, int | None]:
    value = str(text or "")
    if not value:
        return None, None

    numbers = []
    for match in re.finditer(r"(?<!\w)(\d{2,3}(?:,\d{3})?|\d{2,3}k)(?!\w)", value, re.IGNORECASE):
        raw = match.group(1).replace(",", "").lower()
        amount = int(float(raw[:-1]) * 1000) if raw.endswith("k") else int(raw)
        if amount < 1000:
            amount *= 1000
        if amount >= 20000:
            numbers.append(amount)

    if not numbers:
        return None, None
    if len(numbers) == 1:
        return numbers[0], numbers[0]
    return min(numbers[:2]), max(numbers[:2])


def _parse_iso_date(value: Any) -> str:
    if not value:
        return date.today().isoformat()
    try:
        normalized = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(normalized).date().isoformat()
    except ValueError:
        return date.today().isoformat()


def _parse_unix_date(value: Any) -> str:
    try:
        return datetime.fromtimestamp(int(value), tz=UTC).date().isoformat()
    except (TypeError, ValueError, OSError):
        return date.today().isoformat()


def _safe_int(value: Any) -> int | None:
    try:
        amount = int(value)
    except (TypeError, ValueError):
        return None
    return amount if amount > 0 else None


def _rate_job(
    salary_min: int | None,
    salary_max: int | None,
    posted_at: str,
    remote: bool,
    has_description: bool,
) -> float:
    salary = salary_max or salary_min or 0
    score = 3.0
    if salary >= 200000:
        score += 1.0
    elif salary >= 140000:
        score += 0.7
    elif salary >= 90000:
        score += 0.4
    if _days_old(posted_at) <= 14:
        score += 0.5
    elif _days_old(posted_at) <= 45:
        score += 0.25
    if remote:
        score += 0.2
    if has_description:
        score += 0.2
    return round(min(score, 5.0), 1)


def _days_old(posted_at: str) -> int:
    try:
        posted = date.fromisoformat(posted_at)
    except ValueError:
        return 999
    return max((date.today() - posted).days, 0)


PROVIDERS.extend([_fetch_remotive, _fetch_arbeitnow, _fetch_remoteok])
