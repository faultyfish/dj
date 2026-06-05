# store.py — Job persistence: upsert + query helpers

from __future__ import annotations
import logging
from typing import List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from models import Job
from database import JobRecord

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------

def job_to_record(job: Job) -> dict:
    """Convert a Job dataclass into a dict suitable for DB insert."""
    return {
        "title":       job.title,
        "company":     job.company,
        "location":    job.location,
        "source":      job.source,
        "job_url":     job.job_url,
        "description": job.description[:10_000],  # guard against huge blobs
        "job_type":    job.job_type,
        "salary":      job.salary,
        "score":       job.score,
        "date_posted": job.date_posted,
        "scraped_at":  job.scraped_at,
        "fingerprint": job.fingerprint,
    }


def record_to_job(record: JobRecord) -> Job:
    """Convert a DB row back into a Job dataclass."""
    return Job(
        id=record.id,
        title=record.title,
        company=record.company,
        location=record.location,
        source=record.source,
        job_url=record.job_url,
        description=record.description or "",
        job_type=record.job_type or "",
        salary=record.salary or "",
        score=record.score or 0,
        date_posted=record.date_posted,
        scraped_at=record.scraped_at,
    )


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------

def upsert_jobs(session: Session, jobs: List[Job]) -> Tuple[int, int]:
    """
    Insert jobs that don't exist yet; skip (do nothing) on duplicate fingerprint.
    Returns (inserted_count, skipped_count).
    """
    if not jobs:
        return 0, 0

    rows = [job_to_record(j) for j in jobs]

    stmt = (
        pg_insert(JobRecord)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["fingerprint"])
    )

    result = session.execute(stmt)
    session.commit()

    inserted = result.rowcount if result.rowcount != -1 else len(rows)
    skipped = len(rows) - inserted

    logger.info("Upsert complete — inserted: %d, skipped (duplicates): %d", inserted, skipped)
    return inserted, skipped


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def fetch_recent_jobs(session: Session, limit: int = 100, min_score: int = 10) -> List[Job]:
    """Fetch the most recent passing jobs, ordered by scraped_at desc."""
    records = (
        session.query(JobRecord)
        .filter(JobRecord.score >= min_score)
        .order_by(JobRecord.scraped_at.desc())
        .limit(limit)
        .all()
    )
    return [record_to_job(r) for r in records]


def fetch_all_jobs(session: Session, min_score: int = 10) -> List[Job]:
    """Fetch all passing jobs for dashboard generation."""
    records = (
        session.query(JobRecord)
        .filter(JobRecord.score >= min_score)
        .order_by(JobRecord.scraped_at.desc())
        .all()
    )
    return [record_to_job(r) for r in records]


def count_jobs(session: Session) -> int:
    return session.query(JobRecord).count()


def cleanup_old_jobs(session: Session, days_old: int = 30) -> int:
    """
    Delete jobs older than N days (scraped_at cutoff).
    Returns the count of deleted jobs.
    """
    from datetime import datetime, timedelta, timezone
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)
    count = session.query(JobRecord).filter(JobRecord.scraped_at < cutoff).delete()
    session.commit()
    if count:
        logger.info("Cleanup: deleted %d jobs older than %d days", count, days_old)
    return count
