from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt

from app.schemas import JobGroup, JobListing, JobSearchRequest, JobSearchResult


SOURCES = [
    "LinkedIn Jobs",
    "Indeed",
    "Glassdoor",
    "ZipRecruiter",
    "Wellfound",
    "RemoteOK",
]


@dataclass(frozen=True)
class RawJob:
    id: str
    title: str
    company: str
    location: str
    latitude: float | None
    longitude: float | None
    source: str
    source_url: str
    salary_min: int | None
    salary_max: int | None
    rating: float
    job_type: str
    remote: bool
    posted_at: str
    summary: str


RAW_JOBS = [
    RawJob(
        id="linkedin-senior-ai-engineer-nyc",
        title="Senior AI Engineer",
        company="Northstar Analytics",
        location="New York, NY",
        latitude=40.7128,
        longitude=-74.0060,
        source="LinkedIn Jobs",
        source_url="https://www.linkedin.com/jobs/search/?keywords=Senior%20AI%20Engineer",
        salary_min=185000,
        salary_max=245000,
        rating=4.7,
        job_type="Full-time",
        remote=False,
        posted_at="2026-06-01",
        summary="Build production retrieval and ranking systems for financial research workflows.",
    ),
    RawJob(
        id="indeed-platform-engineer-nyc",
        title="Platform Engineer",
        company="Hudson Cloud Labs",
        location="New York, NY",
        latitude=40.7128,
        longitude=-74.0060,
        source="Indeed",
        source_url="https://www.indeed.com/jobs?q=Platform+Engineer&l=New+York%2C+NY",
        salary_min=155000,
        salary_max=210000,
        rating=4.3,
        job_type="Full-time",
        remote=False,
        posted_at="2026-05-29",
        summary="Own Kubernetes, observability, and developer platform automation.",
    ),
    RawJob(
        id="glassdoor-product-designer-nyc",
        title="Product Designer",
        company="MetroHealth Digital",
        location="New York, NY",
        latitude=40.7128,
        longitude=-74.0060,
        source="Glassdoor",
        source_url="https://www.glassdoor.com/Job/new-york-product-designer-jobs-SRCH_IL.0,8_IC1132348_KO9,25.htm",
        salary_min=130000,
        salary_max=175000,
        rating=4.5,
        job_type="Full-time",
        remote=False,
        posted_at="2026-05-31",
        summary="Design patient-facing digital experiences and research-backed product flows.",
    ),
    RawJob(
        id="ziprecruiter-data-engineer-austin",
        title="Data Engineer",
        company="Lone Star Mobility",
        location="Austin, TX",
        latitude=30.2672,
        longitude=-97.7431,
        source="ZipRecruiter",
        source_url="https://www.ziprecruiter.com/jobs-search?search=Data+Engineer&location=Austin%2C+TX",
        salary_min=145000,
        salary_max=195000,
        rating=4.4,
        job_type="Full-time",
        remote=False,
        posted_at="2026-05-28",
        summary="Model fleet telemetry and build reliable analytics pipelines.",
    ),
    RawJob(
        id="wellfound-full-stack-sf",
        title="Full Stack Engineer",
        company="SeedDeck",
        location="San Francisco, CA",
        latitude=37.7749,
        longitude=-122.4194,
        source="Wellfound",
        source_url="https://wellfound.com/jobs",
        salary_min=170000,
        salary_max=230000,
        rating=4.6,
        job_type="Full-time",
        remote=False,
        posted_at="2026-05-30",
        summary="Ship TypeScript and Python features across an early-stage fundraising platform.",
    ),
    RawJob(
        id="remoteok-ml-platform-remote",
        title="Machine Learning Platform Engineer",
        company="Orbit Remote",
        location="Remote - United States",
        latitude=None,
        longitude=None,
        source="RemoteOK",
        source_url="https://remoteok.com/remote-machine-learning-jobs",
        salary_min=165000,
        salary_max=225000,
        rating=4.8,
        job_type="Remote",
        remote=True,
        posted_at="2026-06-02",
        summary="Scale model deployment, feature stores, and monitoring across remote-first teams.",
    ),
    RawJob(
        id="linkedin-frontend-chicago",
        title="Frontend Engineer",
        company="Great Lakes Commerce",
        location="Chicago, IL",
        latitude=41.8781,
        longitude=-87.6298,
        source="LinkedIn Jobs",
        source_url="https://www.linkedin.com/jobs/search/?keywords=Frontend%20Engineer&location=Chicago",
        salary_min=125000,
        salary_max=168000,
        rating=4.1,
        job_type="Hybrid",
        remote=False,
        posted_at="2026-05-27",
        summary="Modernize React commerce surfaces and shared design-system components.",
    ),
    RawJob(
        id="indeed-devops-atlanta",
        title="DevOps Engineer",
        company="Peachtree Robotics",
        location="Atlanta, GA",
        latitude=33.7490,
        longitude=-84.3880,
        source="Indeed",
        source_url="https://www.indeed.com/jobs?q=DevOps+Engineer&l=Atlanta%2C+GA",
        salary_min=135000,
        salary_max=182000,
        rating=4.2,
        job_type="Hybrid",
        remote=False,
        posted_at="2026-05-26",
        summary="Automate CI/CD, cloud infrastructure, and factory telemetry deployments.",
    ),
]


def scan_jobs(body: JobSearchRequest) -> JobSearchResult:
    query = body.query.strip()
    location_label = _clean_location_label(body)
    listings = [_to_listing(job, body) for job in RAW_JOBS if _matches(job, body, query)]
    listings.sort(key=_job_sort_key)
    groups = _group_jobs(listings)

    return JobSearchResult(
        query=query,
        location_label=location_label,
        sources_scanned=SOURCES,
        total_results=len(listings),
        groups=groups,
    )


def _matches(job: RawJob, body: JobSearchRequest, query: str) -> bool:
    if not _matches_query(job, query):
        return False
    if job.remote and body.include_remote:
        return True
    if body.latitude is not None and body.longitude is not None:
        distance = _distance_miles(body.latitude, body.longitude, job.latitude, job.longitude)
        return distance is not None and distance <= body.radius_miles
    if body.location_label:
        return _matches_location_label(job.location, body.location_label)
    return True


def _matches_query(job: RawJob, query: str) -> bool:
    terms = [term for term in query.lower().replace(",", " ").split() if term]
    if not terms:
        return True
    haystack = f"{job.title} {job.company} {job.summary}".lower()
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


def _to_listing(job: RawJob, body: JobSearchRequest) -> JobListing:
    distance = None
    if body.latitude is not None and body.longitude is not None and job.latitude and job.longitude:
        distance = round(_distance_miles(body.latitude, body.longitude, job.latitude, job.longitude) or 0, 1)

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
        distance_miles=distance,
        posted_at=job.posted_at,
        summary=job.summary,
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


def _distance_miles(
    origin_latitude: float,
    origin_longitude: float,
    job_latitude: float | None,
    job_longitude: float | None,
) -> float | None:
    if job_latitude is None or job_longitude is None:
        return None

    lat1, lon1, lat2, lon2 = map(radians, [origin_latitude, origin_longitude, job_latitude, job_longitude])
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return 3958.8 * 2 * asin(sqrt(a))
