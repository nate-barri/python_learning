import os
import time
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database import Team, Match, Event, Standing, Player, PlayerStat, Base

load_dotenv()

API_KEY  = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
SEASON   = 2022  # switch to 2026 when you upgrade your plan

DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine  = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)

# Endpoints that do NOT accept a season parameter
NO_SEASON_ENDPOINTS = {
    "fixtures/events",
    "fixtures/lineups",
    "fixtures/statistics",
    "fixtures/players"
}


def api_get(endpoint, params={}):
    """Central API call function — checks errors and remaining quota."""
    if endpoint not in NO_SEASON_ENDPOINTS:
        params["season"] = SEASON

    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        params=params,
        headers={"x-apisports-key": API_KEY}
    )
    data = response.json()

    if data.get("errors"):
        print(f"  API error on /{endpoint}: {data['errors']}")
        return []

    remaining = response.headers.get("x-ratelimit-requests-remaining", "?")
    print(f"  /{endpoint} — {data['results']} results | {remaining} requests remaining today")

    return data["response"]


# --- Step 1: Fetch and save all teams ---
def fetch_teams():
    print("\nFetching teams...")
    results = api_get("teams", {"league": 1})

    session = Session()
    saved = 0

    for entry in results:
        t = entry["team"]

        existing = session.get(Team, t["id"])
        if existing:
            continue

        team = Team(
            team_id  = t["id"],
            name     = t["name"],
            code     = t.get("code"),
            country  = t.get("country"),
            logo_url = t.get("logo")
        )
        session.add(team)
        saved += 1

    session.commit()
    session.close()
    print(f"  Saved {saved} teams to database.")


# --- Step 2: Fetch and save all fixtures ---
def fetch_fixtures():
    print("\nFetching fixtures...")
    results = api_get("fixtures", {"league": 1})

    session = Session()
    saved = 0

    for entry in results:
        f     = entry["fixture"]
        teams = entry["teams"]
        goals = entry["goals"]

        existing = session.get(Match, f["id"])
        if existing:
            # Update status and score if match already exists
            existing.status     = f["status"]["short"]
            existing.elapsed    = f["status"]["elapsed"]
            existing.home_goals = goals.get("home")
            existing.away_goals = goals.get("away")
            continue

        match = Match(
            fixture_id   = f["id"],
            date         = f["date"],
            venue        = f["venue"]["name"],
            city         = f["venue"]["city"],
            status       = f["status"]["short"],
            elapsed      = f["status"]["elapsed"],
            round        = entry["league"]["round"],
            home_team_id = teams["home"]["id"],
            away_team_id = teams["away"]["id"],
            home_goals   = goals.get("home"),
            away_goals   = goals.get("away")
        )
        session.add(match)
        saved += 1

    session.commit()
    session.close()
    print(f"  Saved {saved} fixtures to database.")


# --- Step 3: Fetch and save standings ---
def fetch_standings():
    print("\nFetching standings...")
    results = api_get("standings", {"league": 1})

    if not results:
        print("  No standings data available yet.")
        return

    session = Session()
    saved = 0

    # Standings come back as a list of groups
    all_groups = results[0]["league"]["standings"]

    for group in all_groups:
        for entry in group:
            team_id    = entry["team"]["id"]
            group_name = entry["group"]

            existing = session.query(Standing).filter_by(team_id=team_id).first()
            if existing:
                existing.rank          = entry["rank"]
                existing.points        = entry["points"]
                existing.played        = entry["all"]["played"]
                existing.won           = entry["all"]["win"]
                existing.drawn         = entry["all"]["draw"]
                existing.lost          = entry["all"]["lose"]
                existing.goals_for     = entry["all"]["goals"]["for"]
                existing.goals_against = entry["all"]["goals"]["against"]
                existing.goal_diff     = entry["goalsDiff"]
                existing.form          = entry.get("form")
                continue

            standing = Standing(
                team_id       = team_id,
                group_name    = group_name,
                rank          = entry["rank"],
                points        = entry["points"],
                played        = entry["all"]["played"],
                won           = entry["all"]["win"],
                drawn         = entry["all"]["draw"],
                lost          = entry["all"]["lose"],
                goals_for     = entry["all"]["goals"]["for"],
                goals_against = entry["all"]["goals"]["against"],
                goal_diff     = entry["goalsDiff"],
                form          = entry.get("form")
            )
            session.add(standing)
            saved += 1

    session.commit()
    session.close()
    print(f"  Saved {saved} standings to database.")


# --- Step 4: Fetch events for all finished or live matches ---
def fetch_all_events():
    print("\nFetching events for completed and live matches...")

    session = Session()
    finished_statuses = ["FT", "AET", "PEN", "1H", "2H", "HT", "ET", "P"]
    matches = session.query(Match).filter(
        Match.status.in_(finished_statuses)
    ).all()
    fixture_ids = [m.fixture_id for m in matches]
    session.close()

    print(f"  Found {len(fixture_ids)} matches to fetch events for.")

    for fixture_id in fixture_ids:
        results = api_get("fixtures/events", {"fixture": fixture_id})

        if not results:
            # If rate limited, wait 60 seconds before continuing
            print("  Rate limit hit — waiting 60 seconds...")
            time.sleep(60)
            continue

        session = Session()
        saved = 0

        for entry in results:
            existing = session.query(Event).filter_by(
                fixture_id  = fixture_id,
                minute      = entry["time"]["elapsed"],
                player_name = entry["player"]["name"],
                event_type  = entry["type"]
            ).first()

            if existing:
                continue

            event = Event(
                fixture_id   = fixture_id,
                minute       = entry["time"]["elapsed"],
                extra_minute = entry["time"].get("extra"),
                team_id      = entry["team"]["id"],
                player_name  = entry["player"]["name"],
                assist_name  = entry["assist"].get("name") if entry.get("assist") else None,
                event_type   = entry["type"],
                detail       = entry["detail"]
            )
            session.add(event)
            saved += 1

        session.commit()
        session.close()
        print(f"  Saved {saved} events for fixture {fixture_id}.")

        # Wait 2 seconds between each request to stay within the per-minute limit
        time.sleep(2)


# --- Step 5: Fetch player stats for all finished matches ---
def fetch_player_stats():
    print("\nFetching player stats for completed matches...")

    session = Session()
    finished_statuses = ["FT", "AET", "PEN"]
    matches = session.query(Match).filter(
        Match.status.in_(finished_statuses)
    ).all()
    fixture_ids = [m.fixture_id for m in matches]
    session.close()

    print(f"  Found {len(fixture_ids)} finished matches.")

    for fixture_id in fixture_ids:
        results = api_get("fixtures/players", {"fixture": fixture_id})

        if not results:
            print("  Rate limit hit — waiting 60 seconds...")
            time.sleep(60)
            continue

        session = Session()
        saved = 0

        for team_entry in results:
            for p in team_entry.get("players", []):
                info  = p["player"]
                stats = p["statistics"][0] if p.get("statistics") else {}

                # Skip if already saved for this fixture
                existing = session.query(PlayerStat).filter_by(
                    fixture_id = fixture_id,
                    player_id  = info["id"]
                ).first()
                if existing:
                    continue

                # Save player if not already in players table
                existing_player = session.get(Player, info["id"])
                if not existing_player:
                    player = Player(
                        player_id = info["id"],
                        name      = info["name"],
                        photo_url = info.get("photo")
                    )
                    session.add(player)
                    session.flush()

                games    = stats.get("games", {})
                shots    = stats.get("shots", {})
                goals    = stats.get("goals", {})
                passes   = stats.get("passes", {})
                tackles  = stats.get("tackles", {})
                cards    = stats.get("cards", {})

                stat = PlayerStat(
                    fixture_id     = fixture_id,
                    player_id      = info["id"],
                    rating         = float(games.get("rating") or 0),
                    minutes_played = games.get("minutes") or 0,
                    goals          = goals.get("total") or 0,
                    assists        = goals.get("assists") or 0,
                    shots_total    = shots.get("total") or 0,
                    shots_on       = shots.get("on") or 0,
                    passes_total   = passes.get("total") or 0,
                    passes_key     = passes.get("key") or 0,
                    tackles        = tackles.get("total") or 0,
                    yellow_cards   = cards.get("yellow") or 0,
                    red_cards      = cards.get("red") or 0
                )
                session.add(stat)
                saved += 1

        session.commit()
        session.close()
        print(f"  Saved {saved} player stats for fixture {fixture_id}.")
        time.sleep(2)

if __name__ == "__main__":
    fetch_teams()
    fetch_fixtures()
    fetch_standings()
    fetch_all_events()
    fetch_player_stats()