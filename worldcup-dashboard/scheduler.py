import time
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

from database import Match
from fetcher import (
    fetch_teams,
    fetch_fixtures,
    fetch_standings,
    fetch_all_events,
    api_get,
    Session
)

load_dotenv()

# Set up basic logging so you can see what the scheduler is doing
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
    """Runs every 10 minutes — refreshes fixtures and standings."""
    log.info("Running regular update...")
    fetch_fixtures()
    fetch_standings()
    log.info("Regular update complete.")


def startup():
    """Runs once when the scheduler starts."""
    log.info("Running startup fetch...")
    fetch_teams()
    fetch_fixtures()
    fetch_standings()
    log.info("Startup fetch complete.")


if __name__ == "__main__":
    scheduler = BackgroundScheduler()

    # Regular update every 10 minutes
    scheduler.add_job(
        regular_update,
        trigger="interval",
        minutes=10,
        id="regular_update",
        name="Refresh fixtures and standings"
    )

    # Live update every 15 seconds
    scheduler.add_job(
        live_update,
        trigger="interval",
        seconds=15,
        id="live_update",
        name="Fetch live match events"
    )

    # Start the scheduler
    scheduler.start()
    log.info("Scheduler started.")

    # Run startup fetch immediately
    startup()

    log.info("Press Ctrl+C to stop.\n")

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Stopping scheduler...")
        scheduler.shutdown()
        log.info("Scheduler stopped.")