from fastapi.testclient import TestClient

from app.main import app
from app.schemas import JobSearchRequest
from app.services.job_scanner import scan_jobs


def test_scan_jobs_filters_by_location_and_sorts_salary_high_to_low():
    result = scan_jobs(
        JobSearchRequest(
            query="engineer",
            latitude=40.7128,
            longitude=-74.006,
            location_label="New York, NY",
            radius_miles=25,
            include_remote=False,
        )
    )

    salaries = [group.highest_salary for group in result.groups]

    assert result.total_results == 2
    assert salaries == sorted(salaries, reverse=True)
    assert result.groups[0].title == "Senior AI Engineer"
    assert result.groups[0].location == "New York, NY"


def test_scan_jobs_can_include_remote_results_outside_area():
    result = scan_jobs(
        JobSearchRequest(
            query="machine learning engineer",
            latitude=40.7128,
            longitude=-74.006,
            radius_miles=25,
            include_remote=True,
        )
    )

    assert result.total_results == 1
    assert result.groups[0].jobs[0].remote is True
    assert result.groups[0].average_rating == 4.8


def test_job_scanner_api_response_groups_jobs_by_title_and_location():
    client = TestClient(app)
    response = client.post(
        "/api/agents/job-scanner",
        json={
            "query": "product designer",
            "location_label": "New York",
            "radius_miles": 50,
            "include_remote": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_results"] == 1
    assert payload["sources_scanned"] == [
        "LinkedIn Jobs",
        "Indeed",
        "Glassdoor",
        "ZipRecruiter",
        "Wellfound",
        "RemoteOK",
    ]
    assert payload["groups"][0]["title"] == "Product Designer"
    assert payload["groups"][0]["location"] == "New York, NY"
