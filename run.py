# run.py — Entry point: scrape → filter → store → summary

import logging
import sys
from scraper import scrape
from filters import filter_jobs, deduplicate
from database import get_engine, get_session_factory, init_db, migrate_db
from store import upsert_jobs, count_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("job_radar")


def main():
    location = sys.argv[1] if len(sys.argv) > 1 else None

    # 1. Scrape
    raw_jobs = scrape(location)
    if not raw_jobs:
        logger.warning("No jobs returned from scraper. Exiting.")
        return

    # 2. Deduplicate raw results
    unique_jobs = deduplicate(raw_jobs)

    # 3. Filter + score
    kept, rejected = filter_jobs(unique_jobs)

    # 4. Store
    engine = get_engine()
    init_db(engine)
    migrate_db(engine)
    SessionFactory = get_session_factory(engine)

    with SessionFactory() as session:
        inserted, skipped = upsert_jobs(session, kept)
        total_in_db = count_jobs(session)

    # 5. Summary
    print(f"\n{'='*60}")
    print(f"  Dublin Part-Time Job Radar — Run Summary")
    print(f"{'='*60}")
    print(f"  Raw scraped   : {len(raw_jobs)}")
    print(f"  After dedup   : {len(unique_jobs)}")
    print(f"  Kept (pass)   : {len(kept)}")
    print(f"  Rejected      : {len(rejected)}")
    print(f"  DB inserted   : {inserted}")
    print(f"  DB skipped    : {skipped}")
    print(f"  Total in DB   : {total_in_db}")
    print(f"{'='*60}\n")

    print("TOP JOBS (by score):\n")
    for job in sorted(kept, key=lambda j: j.score, reverse=True)[:10]:
        print(f"  [{job.score:+3d}] {job.title} @ {job.company}")
        print(f"        {job.location} | {job.source} | {job.job_type}")
        print(f"        {job.job_url}")
        print()


if __name__ == "__main__":
    main()
