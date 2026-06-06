# filters.py — Confidence-scored job filtering

from __future__ import annotations
import logging
from typing import List, Tuple

from models import Job
from config import ALLOW_RULES, BLOCK_RULES, PASS_THRESHOLD, DUBLIN_KEYWORDS

logger = logging.getLogger(__name__)


def _check_rules(rules: list, title: str, description: str) -> Tuple[int, List[str]]:
    """
    Evaluate a list of rules against a job's title and description.
    Returns (total_score_delta, list_of_reason_strings).
    """
    total = 0
    reasons = []

    for rule in rules:
        keywords: list = rule["keywords"]
        delta: int = rule["score"]
        field: str = rule["field"]  # "title" | "description" | "any"

        if field == "title":
            targets = [title]
        elif field == "description":
            targets = [description]
        else:
            targets = [title, description]

        for keyword in keywords:
            if any(keyword in target for target in targets):
                total += delta
                direction = "✅" if delta > 0 else "❌"
                reasons.append(f"{direction} '{keyword}' ({delta:+d})")
                break  # one keyword per rule is enough

    return total, reasons


def score_job(job: Job) -> Job:
    """
    Score a single job in-place. Returns the job for chaining.
    Combines signals from:
      - job_type field (direct part-time flag)
      - title keywords
      - description keywords
    """
    title = job.title.lower()
    description = job.description.lower()
    reasons: List[str] = []
    total = 0

    # Direct part-time flag from job_type field (most reliable signal)
    if job.job_type and "part" in job.job_type.lower():
        total += 20
        reasons.append("✅ job_type field is part-time (+20)")

    allow_score, allow_reasons = _check_rules(ALLOW_RULES, title, description)
    block_score, block_reasons = _check_rules(BLOCK_RULES, title, description)

    total += allow_score + block_score
    reasons += allow_reasons + block_reasons

    job.score = total
    job.score_reasons = reasons
    return job


def filter_jobs(jobs: List[Job]) -> Tuple[List[Job], List[Job]]:
    """
    Score all jobs, then split into (kept, rejected).
    Logs a summary and the score breakdown for every rejected job.
    """
    kept = []
    rejected = []

    for job in jobs:
        score_job(job)
        if job.score >= PASS_THRESHOLD:
            kept.append(job)
        else:
            rejected.append(job)
            logger.debug(
                "REJECTED [score=%d] %s @ %s | %s",
                job.score, job.title, job.company, job.score_reasons
            )

    logger.info(
        "Filtering complete — kept %d / %d  (rejected %d)",
        len(kept), len(jobs), len(rejected)
    )
    return kept, rejected


def deduplicate(jobs: List[Job]) -> List[Job]:
    """
    Remove duplicate jobs by fingerprint (title+company).
    Keeps the first occurrence (earliest in list = most recent scrape order).
    """
    seen = set()
    unique = []
    for job in jobs:
        fp = job.fingerprint
        if fp not in seen:
            seen.add(fp)
            unique.append(job)
    dupes = len(jobs) - len(unique)
    if dupes:
        logger.info("Deduplicated %d duplicate jobs", dupes)
    return unique


def filter_dublin_only(jobs: List[Job]) -> List[Job]:
    """
    Keep only jobs located in Dublin (case-insensitive).
    Removes jobs from neighbouring counties or elsewhere.
    """
    dublin = []
    non_dublin = []

    for job in jobs:
        loc = job.location.lower()
        if any(keyword in loc for keyword in DUBLIN_KEYWORDS):
            dublin.append(job)
        else:
            non_dublin.append(job)

    if non_dublin:
        logger.info(
            "Filtered out %d non-Dublin jobs (locations: %s)",
            len(non_dublin),
            ", ".join(set(j.location for j in non_dublin[:5]))
        )
    return dublin
