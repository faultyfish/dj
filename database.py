# database.py — SQLAlchemy setup + jobs table schema

from __future__ import annotations
import os
import logging
from datetime import datetime

from sqlalchemy import (
    create_engine, text,
    Column, Integer, String, Text, DateTime, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

logger = logging.getLogger(__name__)

Base = declarative_base()


# ---------------------------------------------------------------------------
# Table definition
# ---------------------------------------------------------------------------

class JobRecord(Base):
    __tablename__ = "jobs"

    id          = Column(Integer, primary_key=True, autoincrement=True)

    # Identity
    title       = Column(String(255), nullable=False)
    company     = Column(String(255), nullable=False)
    location    = Column(String(255))
    source      = Column(String(50))          # "indeed" | "linkedin"
    job_url     = Column(Text)

    # Content
    description = Column(Text, default="")
    job_type    = Column(String(100), default="")
    salary      = Column(String(255), default="")

    # Scoring
    score       = Column(Integer, default=0)

    # Timestamps
    date_posted = Column(DateTime(timezone=True), nullable=True)
    scraped_at  = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Dedup key — same logic as Job.fingerprint
    fingerprint = Column(String(512), nullable=False, unique=True)

    __table_args__ = (
        Index("ix_jobs_scraped_at", "scraped_at"),
        Index("ix_jobs_score",      "score"),
        Index("ix_jobs_source",     "source"),
    )

    def __repr__(self):
        return f"<JobRecord id={self.id} title={self.title!r} company={self.company!r}>"


# ---------------------------------------------------------------------------
# Engine + session factory
# ---------------------------------------------------------------------------

def get_engine(database_url: str | None = None):
    """
    Build a SQLAlchemy engine from DATABASE_URL env var (or explicit argument).
    Neon requires ?sslmode=require — appended automatically if missing.
    """
    url = database_url or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Export it as an environment variable or pass it explicitly."
        )

    # Neon uses postgres:// scheme; SQLAlchemy needs postgresql://
    url = url.replace("postgres://", "postgresql://", 1)

    # Ensure SSL for Neon
    if "sslmode" not in url:
        sep = "&" if "?" in url else "?"
        url += f"{sep}sslmode=require"

    engine = create_engine(
        url,
        pool_pre_ping=True,      # detect stale connections
        pool_size=3,             # small pool — GitHub Actions is single-process
        max_overflow=2,
        echo=False,
    )
    logger.info("Database engine created: %s", engine.url.render_as_string(hide_password=True))
    return engine


def get_session_factory(engine) -> sessionmaker:
    return sessionmaker(bind=engine, expire_on_commit=False)


def init_db(engine):
    """Create all tables if they don't exist."""
    Base.metadata.create_all(engine)
    logger.info("Database tables initialised")
