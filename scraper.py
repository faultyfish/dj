# scraper.py — JobSpy scraping logic

from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import List

from models import Job
from config import SCRAPER

logger = logging.getLogger(__name__)


def _row_to_job(row) -> Job | None:
    """Convert a JobSpy DataFrame row into a Job instance."""
    try:
        # JobSpy returns a pandas Series per row
        title = str(row.get("title") or "").strip()
        company = str(row.get("company") or "").strip()

        if not title or not company:
            return None

        # Normalise date_posted
        date_posted = row.get("date_posted")
        if date_posted is not None:
            try:
                if hasattr(date_posted, "to_pydatetime"):
                    date_posted = date_posted.to_pydatetime()
                if date_posted.tzinfo is None:
                    date_posted = date_posted.replace(tzinfo=timezone.utc)
            except Exception:
                date_posted = None

        # Salary: combine min/max if present, else use interval string
        salary_parts = []
        min_sal = row.get("min_amount")
        max_sal = row.get("max_amount")
        interval = str(row.get("interval") or "")
        currency = str(row.get("currency") or "EUR")

        if min_sal and max_sal:
            salary_parts.append(f"{currency} {min_sal:,.0f}–{max_sal:,.0f}")
            if interval:
                salary_parts.append(f"/ {interval}")
        salary = " ".join(salary_parts)

        return Job(
            title=title,
            company=company,
            location=str(row.get("location") or SCRAPER["locations"][0]),
            source=str(row.get("site") or "unknown"),
            job_url=str(row.get("job_url") or ""),
            description=str(row.get("description") or ""),
            job_type=str(row.get("job_type") or ""),
            salary=salary,
            date_posted=date_posted,
        )
    except Exception as exc:
        logger.warning("Skipped malformed row: %s", exc)
        return None


def scrape(location: str | None = None) -> List[Job]:
    """
    Scrape jobs from all configured sources for the given location.
    Falls back to SCRAPER['locations'][0] if not specified.
    Returns a flat list of Job objects (unfiltered).
    """
    try:
        from jobspy import scrape_jobs  # imported here so the module loads without jobspy installed
    except ImportError:
        raise RuntimeError(
            "jobspy is not installed. Run: pip install python-jobspy"
        )

    target_location = location or SCRAPER["locations"][0]
    logger.info("Scraping %s for '%s'...", SCRAPER["sources"], target_location)

    jobs_out: List[Job] = []

    for source in SCRAPER["sources"]:
        try:
            df = scrape_jobs(
                site_name=[source],
                search_term="part time",
                location=target_location,
                results_wanted=SCRAPER["results_per_source"],
                hours_old=SCRAPER["hours_old"],
                country_indeed=SCRAPER["country"],
                verbose=0,
            )

            if df is None or df.empty:
                logger.warning("No results from %s", source)
                continue

            batch = [_row_to_job(row) for _, row in df.iterrows()]
            valid = [j for j in batch if j is not None]
            logger.info("%s returned %d jobs (%d valid)", source, len(df), len(valid))
            jobs_out.extend(valid)

        except Exception as exc:
            # One source failing must not kill the whole run
            logger.error("Error scraping %s: %s", source, exc, exc_info=True)

    logger.info("Total raw jobs scraped: %d", len(jobs_out))
    return jobs_out
