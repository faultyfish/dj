# models.py — Job data model

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    # Core identity
    title: str
    company: str
    location: str
    source: str                        # "indeed" | "linkedin"
    job_url: str

    # Content
    description: str = ""
    job_type: str = ""                 # e.g. "Part-time", "Full-time"
    salary: str = ""

    # Metadata
    date_posted: Optional[datetime] = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    # Filtering
    score: int = 0
    score_reasons: list = field(default_factory=list)  # human-readable audit trail

    # DB identity (set after insert)
    id: Optional[int] = None

    @property
    def fingerprint(self) -> str:
        """Stable dedup key — normalise before hashing."""
        title = self.title.lower().strip()
        company = self.company.lower().strip()
        return f"{title}|{company}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "source": self.source,
            "job_url": self.job_url,
            "description": self.description,
            "job_type": self.job_type,
            "salary": self.salary,
            "date_posted": self.date_posted.isoformat() if self.date_posted else None,
            "scraped_at": self.scraped_at.isoformat(),
            "score": self.score,
            "score_reasons": self.score_reasons,
        }
