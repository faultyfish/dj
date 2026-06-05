# tests/test_filters.py — runs in CI without a real DB or scraper

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import Job
from filters import score_job, filter_jobs, deduplicate, filter_dublin_only


def make_job(**kwargs) -> Job:
    defaults = dict(
        title="Test Job", company="Test Co", location="Dublin",
        source="indeed", job_url="http://test", job_type="", description=""
    )
    defaults.update(kwargs)
    return Job(**defaults)


# ---------------------------------------------------------------------------
# Filter tests
# ---------------------------------------------------------------------------

def test_part_time_job_type_boosts_score():
    job = make_job(title="Sales Assistant", job_type="Part-time")
    score_job(job)
    assert job.score >= 10, f"Expected score >= 10, got {job.score}"

def test_retail_title_boosts_score():
    job = make_job(title="Part-Time Shop Assistant", job_type="Part-time")
    score_job(job)
    assert job.score >= 25

def test_senior_engineer_is_rejected():
    job = make_job(title="Senior Software Engineer", job_type="Full-time")
    score_job(job)
    assert job.score < 10, f"Senior engineer should be rejected, score={job.score}"

def test_marketing_manager_is_rejected():
    job = make_job(title="Marketing Manager", job_type="Full-time")
    score_job(job)
    assert job.score < 10

def test_hospitality_role_is_kept():
    job = make_job(title="Barista Part Time", job_type="Part-time")
    score_job(job)
    assert job.score >= 10

def test_description_no_experience_boosts():
    job = make_job(
        title="Warehouse Operative", job_type="Part-time",
        description="No experience required. We will train you."
    )
    score_job(job)
    assert job.score >= 30

def test_commission_only_penalised():
    job = make_job(
        title="Sales Rep Part Time", job_type="Part-time",
        description="Commission only role. Must have own car."
    )
    score_job(job)
    # commission_only penalty should reduce score
    reasons_text = " ".join(job.score_reasons)
    assert "commission only" in reasons_text

def test_filter_jobs_splits_correctly():
    jobs = [
        make_job(title="Part-Time Cashier", job_type="Part-time"),
        make_job(title="Senior Architect", job_type="Full-time"),
        make_job(title="Bar Staff Part Time", job_type="Part-time"),
    ]
    kept, rejected = filter_jobs(jobs)
    assert len(kept) == 2
    assert len(rejected) == 1


# ---------------------------------------------------------------------------
# Dublin location filter tests
# ---------------------------------------------------------------------------

def test_dublin_filter_keeps_dublin_postcodes():
    jobs = [
        make_job(location="Dublin 1"),
        make_job(location="D2"),
        make_job(location="Dublin 6W"),
        make_job(location="Dun Laoghaire"),
    ]
    dublin = filter_dublin_only(jobs)
    assert len(dublin) == 4

def test_dublin_filter_removes_non_dublin():
    jobs = [
        make_job(location="Dublin 1"),
        make_job(location="Cork"),
        make_job(location="Limerick"),
        make_job(location="Galway"),
    ]
    dublin = filter_dublin_only(jobs)
    assert len(dublin) == 1
    assert dublin[0].location == "Dublin 1"

def test_dublin_filter_case_insensitive():
    jobs = [
        make_job(location="DUBLIN 5"),
        make_job(location="dublin 7"),
        make_job(location="Dublin 12"),
    ]
    dublin = filter_dublin_only(jobs)
    assert len(dublin) == 3


# ---------------------------------------------------------------------------

def test_dedup_removes_exact_duplicates():
    jobs = [
        make_job(title="Part-Time Cashier", company="Tesco"),
        make_job(title="Part-Time Cashier", company="Tesco"),   # dupe
        make_job(title="Bar Staff", company="O'Briens"),
    ]
    unique = deduplicate(jobs)
    assert len(unique) == 2

def test_dedup_case_insensitive():
    jobs = [
        make_job(title="PART-TIME CASHIER", company="Tesco"),
        make_job(title="part-time cashier", company="tesco"),   # same after normalise
    ]
    unique = deduplicate(jobs)
    assert len(unique) == 1

def test_dedup_different_companies_kept():
    jobs = [
        make_job(title="Warehouse Operative", company="Amazon"),
        make_job(title="Warehouse Operative", company="Lidl"),  # different company
    ]
    unique = deduplicate(jobs)
    assert len(unique) == 2


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  ✅  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌  {t.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
