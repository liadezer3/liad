from fastapi.testclient import TestClient

from app.main import app
from app.schemas import JobSearchRequest
from app.services import job_scanner
from app.services.job_scanner import RawJob, scan_jobs


def sample_jobs(query: str):
    return [
        RawJob(
            id="live-1",
            title="Senior AI Engineer",
            company="Northstar Analytics",
            location="New York, NY",
            source="Remotive",
            source_url="https://remotive.com/remote-jobs/software-dev/senior-ai-engineer-1",
            salary_min=185000,
            salary_max=245000,
            rating=4.9,
            job_type="Full-time",
            remote=False,
            posted_at="2026-06-08",
            summary="Build production AI search systems.",
            description="Build production AI search systems with Python, vector databases, and ranking services.",
        ),
        RawJob(
            id="live-2",
            title="Platform Engineer",
            company="Hudson Cloud Labs",
            location="New York, NY",
            source="Arbeitnow",
            source_url="https://www.arbeitnow.com/jobs/companies/hudson-cloud-labs/platform-engineer",
            salary_min=155000,
            salary_max=210000,
            rating=4.4,
            job_type="Full-time",
            remote=False,
            posted_at="2026-06-07",
            summary="Own Kubernetes and developer platform automation.",
            description="Own Kubernetes, observability, and developer platform automation for engineering teams.",
        ),
        RawJob(
            id="live-3",
            title="Machine Learning Engineer",
            company="Orbit Remote",
            location="Remote - United States",
            source="RemoteOK",
            source_url="https://remoteok.com/remote-jobs/remote-machine-learning-engineer-orbit",
            salary_min=165000,
            salary_max=225000,
            rating=4.8,
            job_type="Remote",
            remote=True,
            posted_at="2026-06-06",
            summary="Scale model deployment and monitoring.",
            description="Scale model deployment, feature stores, and model monitoring for a remote-first team.",
        ),
        RawJob(
            id="stale-1",
            title="Legacy Engineer",
            company="Old Jobs Inc",
            location="New York, NY",
            source="Remotive",
            source_url="https://remotive.com/remote-jobs/software-dev/legacy-engineer",
            salary_min=250000,
            salary_max=300000,
            rating=5.0,
            job_type="Full-time",
            remote=False,
            posted_at="2024-05-01",
            summary="An old listing that should not be returned.",
            description="An old listing that should not be returned.",
        ),
    ]


def test_scan_jobs_filters_by_location_and_sorts_salary_high_to_low(monkeypatch):
    monkeypatch.setattr(job_scanner, "_fetch_live_jobs", sample_jobs)
    result = scan_jobs(
        JobSearchRequest(
            query="engineer",
            location_label="New York, NY",
            radius_miles=25,
            include_remote=False,
        )
    )

    salaries = [group.highest_salary for group in result.groups]

    assert result.total_results == 2
    assert salaries == sorted(salaries, reverse=True)
    assert all(group.title != "Legacy Engineer" for group in result.groups)
    assert result.groups[0].title == "Senior AI Engineer"
    assert result.groups[0].location == "New York, NY"
    assert result.groups[0].jobs[0].description.startswith("Build production AI search")
    assert result.groups[0].jobs[0].source_url.startswith("https://remotive.com/")


def test_scan_jobs_can_include_remote_results_outside_area(monkeypatch):
    monkeypatch.setattr(job_scanner, "_fetch_live_jobs", sample_jobs)
    result = scan_jobs(
        JobSearchRequest(
            query="machine learning engineer",
            location_label="New York, NY",
            radius_miles=25,
            include_remote=True,
        )
    )

    assert result.total_results == 1
    assert result.groups[0].jobs[0].remote is True
    assert result.groups[0].average_rating == 4.8


def test_job_scanner_api_response_groups_jobs_by_title_and_location(monkeypatch):
    monkeypatch.setattr(job_scanner, "_fetch_live_jobs", sample_jobs)
    client = TestClient(app)
    response = client.post(
        "/api/agents/job-scanner",
        json={
            "query": "platform engineer",
            "location_label": "New York",
            "radius_miles": 50,
            "include_remote": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_results"] == 1
    assert payload["sources_scanned"] == ["Remotive", "Arbeitnow", "RemoteOK"]
    assert payload["groups"][0]["title"] == "Platform Engineer"
    assert payload["groups"][0]["location"] == "New York, NY"
    assert payload["groups"][0]["jobs"][0]["description"].startswith("Own Kubernetes")
