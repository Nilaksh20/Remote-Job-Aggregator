import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from dotenv import load_dotenv
from flask import Flask, render_template


# Load environment variables from .env (API keys, config, etc.)
load_dotenv()

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Standard Internal Job Format
# ---------------------------------------------------------------------------
#
# All job data from every API must be normalized into this exact Python
# dictionary structure. This unified format allows the rest of the application
# to work with heterogeneous APIs without needing provider-specific logic.
#
# Format:
# {
#   "id": "unique_job_id",
#   "title": "Job Title",
#   "company": "Company Name",
#   "location": "Location or Remote",
#   "url": "Original job application link",
#   "category": "Software Engineering | Data Science | AI/ML | Internship",
#   "source": "API name",
#   "published": "ISO date string or empty"
# }


# ---------------------------------------------------------------------------
# Categorization and Utility Helpers
# ---------------------------------------------------------------------------


def categorize_job(title: str) -> str:
    """
    Categorize a job title into a high-level bucket using keyword matching.

    This normalization step ensures consistent categorization across all APIs,
    regardless of how each provider structures their job data.

    Order matters: a "Data Science Intern" should be marked as Internship,
    not Data Science, so we check for internships first.
    """
    t = title.lower()

    if "intern" in t or "internship" in t:
        return "Internship"

    if "data" in t or "analyst" in t:
        return "Data Science"

    if "ai" in t or "ml" in t or "machine learning" in t:
        return "AI/ML"

    return "Software Engineering"


def slug_for_category(category: str) -> str:
    """
    Generate a CSS-friendly slug from a category label.

    Example:
    "AI/ML" -> "ai-ml"
    "Software Engineering" -> "software-engineering"
    """
    return (
        category.lower()
        .replace("/", "-")
        .replace(" ", "-")
    )


def generate_job_id(title: str, company: str, source: str) -> str:
    """
    Generate a unique job ID from title, company, and source.

    This creates a stable identifier for deduplication purposes.
    """
    combined = f"{source}:{title}:{company}".lower().strip()
    return hashlib.md5(combined.encode()).hexdigest()[:16]


def parse_iso_datetime(value: Optional[str]) -> Optional[str]:
    """
    Parse and normalize datetime strings to ISO format.

    Different APIs return dates in various formats. This function normalizes
    them to ISO 8601 strings (YYYY-MM-DDTHH:MM:SS) for consistent handling.

    Returns empty string if parsing fails, as per the standard format spec.
    """
    if not value:
        return ""

    try:
        # Handle common ISO variants
        dt_str = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(dt_str)
        return dt.isoformat()
    except Exception:
        # If parsing fails, return empty string per spec
        return ""


# ---------------------------------------------------------------------------
# External API providers
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# External API Providers
# ---------------------------------------------------------------------------
#
# Each function below fetches jobs from a specific public job API and
# normalizes the response into the STANDARD INTERNAL JOB FORMAT.
#
# These functions handle:
# - API authentication (via environment variables)
# - Error handling (fail gracefully if API is unavailable)
# - Field mapping (different APIs use different field names)
# - Data validation (skip incomplete entries)


def fetch_remotive_jobs() -> List[Dict[str, Any]]:
    """
    Fetch remote-friendly tech jobs from the Remotive public API.

    Remotive does not require an API key for read-only access to jobs.
    This makes it an ideal primary source for the aggregation system.

    API Documentation: https://remotive.com/api-documentation
    """
    # Remotive API endpoint - no search params needed, returns all jobs
    url = "https://remotive.com/api/remote-jobs"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        # Log error for debugging (in production, use proper logging)
        print(f"Remotive API error: {e}")
        return []

    payload = response.json()
    # Remotive returns jobs directly in the response, or in a 'jobs' key
    items = payload.get("jobs", []) or (payload if isinstance(payload, list) else [])

    jobs: List[Dict[str, Any]] = []
    for item in items:
        # Handle both dict and direct field access
        if not isinstance(item, dict):
            continue
            
        title = (item.get("title") or "").strip()
        company = (item.get("company_name") or item.get("company") or "").strip()
        location = (item.get("candidate_required_location") or item.get("location") or "Remote").strip()
        url = (item.get("url") or item.get("job_url") or "").strip()

        if not title or not company or not url:
            continue

        job_id = generate_job_id(title, company, "Remotive")
        published = parse_iso_datetime(item.get("publication_date") or item.get("published_at"))
        category = categorize_job(title)

        jobs.append({
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "category": category,
            "source": "Remotive",
            "published": published,
        })

    print(f"Remotive: Fetched {len(jobs)} jobs")
    return jobs


def fetch_adzuna_jobs() -> List[Dict[str, Any]]:
    """
    Fetch jobs from the Adzuna API using free API credentials.

    Adzuna aggregates job listings from multiple sources globally.
    Requires APP_ID and APP_KEY from environment variables.

    API Documentation: https://developer.adzuna.com/overview
    """
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    if not app_id or not app_key:
        return []

    # Adzuna requires a country code. Using 'us' as default, but can be configured.
    country = os.getenv("ADZUNA_COUNTRY", "us")
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": 50,
        "what": "software engineer OR developer OR data scientist OR machine learning",
        "content-type": "application/json",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"  Adzuna API error: {str(e)[:100]}")
        return []

    payload = response.json()
    items = payload.get("results", []) or []

    jobs: List[Dict[str, Any]] = []
    for item in items:
        title = (item.get("title") or "").strip()
        company = (item.get("company", {}).get("display_name") or item.get("company", {}).get("name") or "").strip()
        location = (item.get("location", {}).get("display_name") or item.get("location", {}).get("area", [""])[0] or "Remote").strip()
        url = (item.get("redirect_url") or item.get("url") or "").strip()

        if not title or not company or not url:
            continue

        job_id = generate_job_id(title, company, "Adzuna")
        published = parse_iso_datetime(item.get("created"))
        category = categorize_job(title)

        jobs.append({
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "category": category,
            "source": "Adzuna",
            "published": published,
        })

    return jobs


def fetch_jsearch_jobs() -> List[Dict[str, Any]]:
    """
    Fetch jobs from the JSearch API via RapidAPI.

    JSearch aggregates jobs from multiple sources. Requires RAPIDAPI_KEY
    from environment variables.

    API Documentation: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch/
    """
    rapidapi_key = os.getenv("RAPIDAPI_KEY")
    rapidapi_host = os.getenv("JSEARCH_RAPIDAPI_HOST", "jsearch.p.rapidapi.com")

    if not rapidapi_key:
        # JSearch is optional; if the key is missing, we skip this provider.
        return []

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": rapidapi_host,
    }
    params = {
        # Broad but tech-leaning query; adjust as desired.
        "query": "software developer OR data scientist OR machine learning engineer",
        "page": 1,
        "num_pages": 1,
        "date_posted": "month",  # last 30 days
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
    except Exception:
        return []

    payload = response.json()
    items = payload.get("data", []) or []

    jobs: List[Dict[str, Any]] = []
    for item in items:
        title = (item.get("job_title") or "").strip()
        company = (item.get("employer_name") or "").strip()
        location_parts = []
        if item.get("job_city"):
            location_parts.append(item.get("job_city"))
        if item.get("job_state"):
            location_parts.append(item.get("job_state"))
        if item.get("job_country"):
            location_parts.append(item.get("job_country"))
        location = ", ".join(location_parts) if location_parts else "Remote"
        location = location.strip()
        url = (item.get("job_apply_link") or item.get("job_url") or "").strip()

        if not title or not company or not url:
            continue

        job_id = generate_job_id(title, company, "JSearch")
        published = parse_iso_datetime(
            item.get("job_posted_at_datetime_utc") or item.get("job_posted_at")
        )
        category = categorize_job(title)

        jobs.append({
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "category": category,
            "source": "JSearch",
            "published": published,
        })

    return jobs


def fetch_careerjet_jobs() -> List[Dict[str, Any]]:
    """
    Fetch jobs from the Careerjet API.

    Careerjet is a global job search engine. Requires CAREERJET_AFFID
    (affiliate ID) from environment variables. Some endpoints may require
    additional parameters.

    API Documentation: https://www.careerjet.com/partners/api/
    """
    affid = os.getenv("CAREERJET_AFFID")
    locale = os.getenv("CAREERJET_LOCALE", "en_US")
    location = os.getenv("CAREERJET_LOCATION", "")

    if not affid:
        return []

    url = "https://public.api.careerjet.net/search"
    params = {
        "affid": affid,
        "locale_code": locale,
        "keywords": "software engineer OR developer OR data scientist OR machine learning",
        "pagesize": 50,
        "page": 1,
    }

    if location:
        params["location"] = location

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"  Adzuna API error: {str(e)[:100]}")
        return []

    payload = response.json()
    items = payload.get("jobs", []) or []

    jobs: List[Dict[str, Any]] = []
    for item in items:
        title = (item.get("title") or "").strip()
        company = (item.get("company") or "").strip()
        location = (item.get("locations") or item.get("location") or "Remote").strip()
        url = (item.get("url") or item.get("site") or "").strip()

        if not title or not company or not url:
            continue

        job_id = generate_job_id(title, company, "Careerjet")
        published = parse_iso_datetime(item.get("date"))
        category = categorize_job(title)

        jobs.append({
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "category": category,
            "source": "Careerjet",
            "published": published,
        })

    return jobs


def fetch_themuse_jobs() -> List[Dict[str, Any]]:
    """
    Fetch jobs from The Muse API.

    The Muse focuses on startup and tech-focused companies. Limited free
    access available. Requires THEMUSE_API_KEY from environment variables.

    API Documentation: https://www.themuse.com/developers/api/v2
    """
    api_key = os.getenv("THEMUSE_API_KEY")

    if not api_key:
        return []

    url = "https://www.themuse.com/api/public/jobs"
    params = {
        "api_key": api_key,
        "page": 1,
        "category": "Software Engineering,Data Science,Engineering",
        "location": "",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"  Adzuna API error: {str(e)[:100]}")
        return []

    payload = response.json()
    items = payload.get("results", []) or []

    jobs: List[Dict[str, Any]] = []
    for item in items:
        title = (item.get("name") or "").strip()
        company_obj = item.get("company", {})
        company = (company_obj.get("name") or "").strip()
        locations = item.get("locations", [])
        location = locations[0].get("name", "Remote") if locations else "Remote"
        location = location.strip()
        url = (item.get("refs", {}).get("landing_page") or "").strip()

        if not title or not company or not url:
            continue

        job_id = generate_job_id(title, company, "TheMuse")
        published = parse_iso_datetime(item.get("publication_date"))
        category = categorize_job(title)

        jobs.append({
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "category": category,
            "source": "TheMuse",
            "published": published,
        })

    return jobs


def fetch_usajobs() -> List[Dict[str, Any]]:
    """
    Fetch jobs from the USAJobs API (US government jobs).

    USAJobs is a public API for US federal government positions. Requires
    a User-Agent header (no secret key needed). USAJOBS_EMAIL and
    USAJOBS_API_KEY are optional but recommended for higher rate limits.

    API Documentation: https://developer.usajobs.gov/
    """
    email = os.getenv("USAJOBS_EMAIL", "user@example.com")
    api_key = os.getenv("USAJOBS_API_KEY")

    url = "https://data.usajobs.gov/api/Search"
    headers = {
        "User-Agent": email,
        "Host": "data.usajobs.gov",
    }

    if api_key:
        headers["Authorization-Key"] = api_key

    params = {
        "Keyword": "software engineer OR developer OR data scientist OR information technology",
        "ResultsPerPage": 50,
        "Page": 1,
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"  USAJobs API error: {str(e)[:100]}")
        return []

    payload = response.json()
    search_result = payload.get("SearchResult", {})
    items = search_result.get("SearchResultItems", []) or []

    jobs: List[Dict[str, Any]] = []
    for item in items:
        matched_obj = item.get("MatchedObjectDescriptor", {})
        title = (matched_obj.get("PositionTitle") or "").strip()
        org_codes = matched_obj.get("OrganizationCodes", [])
        company = org_codes[0] if org_codes else "US Government"
        company = company.strip()
        position_locations = matched_obj.get("PositionLocationDisplay", [])
        location = position_locations[0] if position_locations else "Remote"
        location = location.strip()
        position_urls = matched_obj.get("PositionURI", [])
        url = position_urls[0] if position_urls else ""
        url = url.strip()

        if not title or not url:
            continue

        job_id = generate_job_id(title, company, "USAJobs")
        published = parse_iso_datetime(matched_obj.get("PublicationStartDate"))
        category = categorize_job(title)

        jobs.append({
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "category": category,
            "source": "USAJobs",
            "published": published,
        })

    return jobs


# ---------------------------------------------------------------------------
# Job Normalization and Aggregation
# ---------------------------------------------------------------------------


def normalize_jobs(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch jobs from all configured APIs and normalize them into a unified stream.

    This is the core aggregation function that:
    1. Calls all fetch functions in parallel (conceptually - sequential for simplicity)
    2. Merges all job lists from different APIs
    3. Removes duplicates based on (title + company) matching
    4. Categorizes jobs using keyword logic
    5. Sorts by published date (newest first)
    6. Limits final list to specified number of jobs

    Why normalization is needed:
    - Different APIs return data in different structures
    - Field names vary (e.g., "title" vs "job_title" vs "name")
    - Date formats differ across providers
    - Some APIs include extra metadata we don't need

    How heterogeneous APIs are unified:
    - Each fetch function maps its API's response to the STANDARD INTERNAL JOB FORMAT
    - All jobs are converted to dictionaries with identical field names
    - Deduplication ensures we don't show the same job twice
    - Categorization provides consistent labels regardless of source
    """
    jobs: List[Dict[str, Any]] = []

    # Fetch from all configured APIs
    # Each function handles its own authentication and error handling
    remotive_jobs = fetch_remotive_jobs()
    jobs.extend(remotive_jobs)
    print(f"✓ Remotive: {len(remotive_jobs)} jobs")
    
    adzuna_jobs = fetch_adzuna_jobs()
    jobs.extend(adzuna_jobs)
    print(f"{'✓' if adzuna_jobs else '✗'} Adzuna: {len(adzuna_jobs)} jobs {'(API keys needed)' if not adzuna_jobs else ''}")
    
    jsearch_jobs = fetch_jsearch_jobs()
    jobs.extend(jsearch_jobs)
    print(f"{'✓' if jsearch_jobs else '✗'} JSearch: {len(jsearch_jobs)} jobs {'(RAPIDAPI_KEY needed)' if not jsearch_jobs else ''}")
    
    careerjet_jobs = fetch_careerjet_jobs()
    jobs.extend(careerjet_jobs)
    print(f"{'✓' if careerjet_jobs else '✗'} Careerjet: {len(careerjet_jobs)} jobs {'(CAREERJET_AFFID needed)' if not careerjet_jobs else ''}")
    
    themuse_jobs = fetch_themuse_jobs()
    jobs.extend(themuse_jobs)
    print(f"{'✓' if themuse_jobs else '✗'} TheMuse: {len(themuse_jobs)} jobs {'(THEMUSE_API_KEY needed)' if not themuse_jobs else ''}")
    
    usajobs_jobs = fetch_usajobs()
    jobs.extend(usajobs_jobs)
    print(f"{'✓' if usajobs_jobs else '✗'} USAJobs: {len(usajobs_jobs)} jobs")

    # Deduplicate: same title + company = same job
    # This prevents showing duplicate listings from different APIs
    seen = set()
    unique_jobs: List[Dict[str, Any]] = []
    for job in jobs:
        # Use title and company as the deduplication key
        key = (job["title"].lower().strip(), job["company"].lower().strip())
        if key in seen:
            continue
        seen.add(key)
        unique_jobs.append(job)

    # Sort by published date (newest first)
    # Jobs without dates fall to the bottom
    def sort_key(job: Dict[str, Any]) -> datetime:
        published = job.get("published", "")
        if not published:
            return datetime.min
        try:
            return datetime.fromisoformat(published.replace("Z", "+00:00"))
        except Exception:
            return datetime.min

    unique_jobs.sort(key=sort_key, reverse=True)

    # Limit to requested number of jobs
    return unique_jobs[:limit]


# ---------------------------------------------------------------------------
# Flask Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """
    Main job discovery page.

    We intentionally fetch fresh jobs on every request so that users always
    see a current snapshot without needing background workers or a database.

    The template expects jobs with category_slug, so we add that field here
    for compatibility with the existing frontend.
    """
    try:
        jobs = normalize_jobs(limit=50)
        
        # Add category_slug for template compatibility
        for job in jobs:
            job["category_slug"] = slug_for_category(job["category"])
        
        # Debug: print number of jobs fetched
        print(f"Fetched {len(jobs)} jobs")
        
        return render_template("index.html", jobs=jobs)
    except Exception as e:
        print(f"Error in index route: {e}")
        import traceback
        traceback.print_exc()
        return render_template("index.html", jobs=[])


if __name__ == "__main__":
    # App entrypoint: run with `python app.py`
    # In production you would typically serve this via a WSGI server.
    app.run(debug=True)


