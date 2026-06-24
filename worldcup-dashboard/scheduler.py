import time
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

from database import Match, Team
from fetcher import (
    fetch_teams,
    fetch_fixtures,
    fetch_standings,
    fetch_all_events,
    api_get,
    Session
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)


def is_match_live():
    """Check if any World Cup match is currently live."""
    live_statuses = {"1H", "2H", "HT", "ET", "P", "BT"}
    session = Session()
    live = session.query(Match).filter(
        Match.status.in_(live_statuses)
    ).count()
    session.close()
    return live > 0


def live_update():
    """Runs every 15 seconds — only fetches events if a match is live."""
    if is_match_live():
        log.info("Live match detected — fetching events...")
        fetch_all_events()
    else:
        log.info("No live matches right now — skipping live update.")


def regular_update():
    """
    Runs every 60 minutes instead of 10.
    Only refreshes fixtures and standings — not teams (rarely changes).
    Saves ~4x requests per hour compared to the old version.
    """
    log.info("Running regular update...")
    fetch_fixtures()
    fetch_standings()
    log.info("Regular update complete.")


def startup():
    """
    Runs once on launch.
    Checks if data already exists before fetching — avoids
    wasting daily quota on data that's already in the database.
    """
    session = Session()
    team_count    = session.query(Team).count()
    match_count   = session.query(Match).count()
    session.close()

    if team_count == 0:
        log.info("No teams found — fetching teams...")
        fetch_teams()
    else:
        log.info(f"Teams already loaded ({team_count} teams) — skipping.")

    if match_count == 0:
        log.info("No fixtures found — fetching fixtures and standings...")
        fetch_fixtures()
        fetch_standings()
    else:
        log.info(f"Fixtures already loaded ({match_count} matches) — skipping.")

    log.info("Startup complete.")


if __name__ == "__main__":
    scheduler = BackgroundScheduler()

    # Regular update every 60 minutes (changed from 10)
    scheduler.add_job(
        regular_update,
        trigger="interval",
        minutes=60,
        id="regular_update",
        name="Refresh fixtures and standings"
    )

    # Live update every 15 seconds — skips automatically if no live matches
    scheduler.add_job(
        live_update,
        trigger="interval",
        seconds=15,
        id="live_update",
        name="Fetch live match events"
    )

    scheduler.start()
    log.info("Scheduler started.")

    # Smart startup — skips if data already exists
    startup()

    log.info("Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Stopping scheduler...")
        scheduler.shutdown()
        log.info("Scheduler stopped.")