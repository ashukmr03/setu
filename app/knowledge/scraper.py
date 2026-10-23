"""
Official scheme scraper — fetches live data from Indian government portals
and prints it as structured records you can paste into schemes.py.

Run this manually to refresh the knowledge base:
    python -m app.knowledge.scraper

Sources:
  - https://www.myscheme.gov.in
  - https://scholarships.gov.in
  - https://www.india.gov.in
  - Karnataka: https://scholarships.karnataka.gov.in

NOTE: This is a one-time / periodic tool, not called during live requests.
It only does GET requests to official government URLs.
"""
import json
import logging
import time
from datetime import date

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}

TODAY = date.today().isoformat()


def _get(url: str, timeout: int = 15) -> BeautifulSoup | None:
    """Safe HTTP GET — returns BeautifulSoup or None on failure."""
    try:
        r = httpx.get(url, headers=_HEADERS, timeout=timeout, follow_redirects=True)
        r.raise_for_status()
        return BeautifulSoup(r.text, "lxml")
    except Exception as e:
        logger.warning("Failed to fetch %s: %s", url, e)
        return None


def scrape_myscheme_scheme(slug: str) -> dict | None:
    """
    Fetch a single scheme page from myscheme.gov.in.
    The site renders server-side HTML with clear section IDs.
    """
    url = f"https://www.myscheme.gov.in/schemes/{slug}"
    soup = _get(url)
    if not soup:
        return None

    title_tag = soup.find("h1") or soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else slug

    def _section(heading_text: str) -> str:
        """Find a section by its heading text."""
        for tag in soup.find_all(["h2", "h3", "h4", "strong", "b"]):
            if heading_text.lower() in tag.get_text(strip=True).lower():
                # Get following sibling paragraph/list text
                sibling = tag.find_next_sibling()
                if sibling:
                    return sibling.get_text(separator=" ", strip=True)
        return ""

    eligibility = _section("eligibility") or _section("who can apply")
    benefits = _section("benefits") or _section("what you get")
    documents = _section("documents") or _section("required documents")
    steps = _section("how to apply") or _section("application process")

    record = {
        "scheme_name": title,
        "category": "General",
        "state_or_national": "National",
        "eligibility": eligibility or "See official URL",
        "benefits": benefits or "See official URL",
        "required_documents": [d.strip() for d in documents.split(",") if d.strip()] or ["See official URL"],
        "application_steps": [steps] if steps else ["Visit official URL"],
        "responsible_department": "Government of India",
        "official_application_url": url,
        "source_url": url,
        "source_page_title": title,
        "last_verified_date": TODAY,
        "verified_by": "setu-scraper-v1",
    }
    logger.info("Scraped: %s", title)
    return record


def scrape_nsp_scheme(scheme_id: str, name: str) -> dict | None:
    """
    Fetch a scholarship detail from scholarships.gov.in (NSP).
    """
    url = f"https://scholarships.gov.in/fresh/schemeDetails.action?schemeId={scheme_id}"
    soup = _get(url)
    if not soup:
        return None

    title_tag = soup.find("h1") or soup.find("title")
    title = name or (title_tag.get_text(strip=True) if title_tag else f"NSP Scheme {scheme_id}")

    # NSP pages have a structured table
    rows: dict[str, str] = {}
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2:
            key = cells[0].get_text(strip=True).lower()
            val = cells[1].get_text(separator=" ", strip=True)
            rows[key] = val

    record = {
        "scheme_name": title,
        "category": "Education / Scholarship",
        "state_or_national": "National",
        "eligibility": rows.get("eligibility", rows.get("who can apply", "See official URL")),
        "benefits": rows.get("benefits", rows.get("amount", "See official URL")),
        "required_documents": [rows.get("documents required", "See official URL")],
        "application_steps": [
            "1. Register at https://scholarships.gov.in",
            "2. Login and select this scheme.",
            "3. Fill the application form and upload documents.",
            "4. Submit for institution verification.",
        ],
        "responsible_department": rows.get("ministry", "Ministry of Education"),
        "official_application_url": "https://scholarships.gov.in",
        "source_url": url,
        "source_page_title": title,
        "last_verified_date": TODAY,
        "verified_by": "setu-scraper-v1",
    }
    logger.info("Scraped NSP: %s", title)
    return record


# ── Target pages to scrape ────────────────────────────────────────────────────
MYSCHEME_SLUGS = [
    "pmkisan",
    "pmjay",
    "pmay-g",
    "ssy",
    "pmmy",
    "pmvishwakarma",
    "mgnregs",
]

NSP_SCHEMES = [
    ("61", "Central Sector Scheme of Scholarships for College Students"),
    ("15", "Post Matric Scholarship for SC Students"),
    ("16", "Post Matric Scholarship for OBC Students"),
]


def run_scraper() -> list[dict]:
    """Run all scrapers and return combined results."""
    results = []

    logger.info("Scraping myscheme.gov.in …")
    for slug in MYSCHEME_SLUGS:
        record = scrape_myscheme_scheme(slug)
        if record:
            results.append(record)
        time.sleep(1)  # polite delay

    logger.info("Scraping scholarships.gov.in …")
    for scheme_id, name in NSP_SCHEMES:
        record = scrape_nsp_scheme(scheme_id, name)
        if record:
            results.append(record)
        time.sleep(1)

    return results


if __name__ == "__main__":
    records = run_scraper()
    print(f"\n✅ Scraped {len(records)} scheme records.\n")
    print(json.dumps(records, ensure_ascii=False, indent=2))
