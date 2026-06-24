# python_learning
will use to learn python

World cup project
Day 1
`Python` | `PostgreSQL` | `API-Football` | `Streamlit`

| **Project** | **World Cup Sports Dashboard** |
|---|---|
| Author | Nathaniel |
| Language | Python 3 |
| Database | PostgreSQL |
| Data Source | API-Football (api-sports.io) |
| Season | 2022 (free tier) / 2026 (paid) |
| Date | June 23, 2026 |

---

## 1. Project Overview

This project is a full-stack sports dashboard built in Python that fetches, stores, and displays FIFA World Cup data. The dashboard pulls live and historical match data from the API-Football REST API, stores it in a PostgreSQL database, and will present it through a Streamlit web interface.

### Architecture at a Glance

| **Layer** | **Technology** |
|---|---|
| Data source | API-Football — api-sports.io |
| Language | Python 3 |
| Database | PostgreSQL via SQLAlchemy ORM |
| Scheduler | APScheduler (background jobs) |
| Dashboard UI | Streamlit (Phase 4 — upcoming) |
| Env config | python-dotenv (.env file) |

### Roadmap

- Phase 1 — Project setup and API access
- Phase 2 — Database design
- Phase 3 — Data fetching and scheduling
- Phase 4 — Streamlit dashboard UI

---

## 2. Project Folder Structure

All project files live inside the `worldcup-dashboard` folder. The `venv` folder is the virtual environment and should never be edited manually.

```
worldcup-dashboard/
│
+-- .env               <- API key and database credentials (never commit this)
+-- .gitignore         <- Excludes .env and venv from version control
+-- test_api.py        <- Initial API connection test
+-- database.py        <- SQLAlchemy table definitions (6 tables)
+-- fetcher.py         <- All API fetch functions
+-- scheduler.py       <- APScheduler automation
│
+-- venv/              <- Virtual environment (do not edit)
```

---

## 3. All pip Installs

All packages are installed inside the virtual environment using the venv pip executable. Always use the full path to `venv/Scripts/pip.exe` on Windows to ensure packages go to the right place.

### Install Command (Windows)

```
& c:/...path.../worldcup-dashboard/venv/Scripts/pip.exe install <package>
```

### Packages Installed

| **Package** | **Purpose** |
|---|---|
| requests | Makes HTTP GET calls to the API-Football REST API |
| pandas | Data manipulation and analysis |
| sqlalchemy | ORM — defines and queries database tables in Python |
| streamlit | Dashboard UI framework (used in Phase 4) |
| python-dotenv | Loads environment variables from the .env file |
| psycopg2-binary | PostgreSQL database driver required by SQLAlchemy |
| apscheduler | Background job scheduler for automated data fetching |

### Full Install Command (all at once)

```
pip install requests pandas sqlalchemy streamlit python-dotenv psycopg2-binary apscheduler
```

---

## 4. Problems Encountered and Fixes

### Problem 1 — API returned 403 Missing Key

```
Error: 403 {'errors': {'token': 'Missing application key. Check our documentation on how to add your API key in headers.'}}
```

**Cause**

The `test_api.py` file was saved inside the `venv/` folder instead of the project root. The `.env` file was not in the same directory as the script, so python-dotenv could not find it and `API_KEY` loaded as `None`.

**Fix**

- Moved `test_api.py` to the `worldcup-dashboard/` root folder
- Confirmed `.env` was in the same folder as the script
- Added a debug line — `print(repr(API_KEY))` — to verify the key was loading correctly before making any API call

---

### Problem 2 — IndexError: list index out of range

```
IndexError: list index out of range
league = data['response'][0]['league']
```

**Cause**

The response array was empty because the free API plan does not include the 2026 season. The code assumed `data['response']` always had at least one item.

**Fix**

- Switched season parameter from `2026` to `2022` (covered by the free tier)
- Added a results check — `if data['results'] > 0` — before accessing the response array

---

### Problem 3 — KeyError: 'season' and KeyError: 'country'

```
KeyError: 'season'
KeyError: 'country'
```

**Cause**

The response object from `/leagues` is nested differently than assumed. The league object only contains `id`, `name`, `type`, and `logo`. The season year lives inside `entry['seasons'][0]['year']` and country lives inside `entry['country']`, not inside `entry['league']`.

**Fix**

```python
entry   = data['response'][0]
league  = entry['league']      # id, name, type, logo
country = entry['country']     # name, code, flag  <- here, not inside league
season  = entry['seasons'][0]  # year, coverage
```

---

### Problem 4 — ModuleNotFoundError: No module named 'psycopg2'

```
ModuleNotFoundError: No module named 'psycopg2'
```

**Cause**

`psycopg2-binary` was not installed inside the virtual environment. Running `pip install` without pointing to the venv pip installs packages into the system Python instead.

**Fix**

```bash
# Always use the venv pip on Windows:
& ...worldcup-dashboard/venv/Scripts/pip.exe install psycopg2-binary
```

---

### Problem 5 — API error: 'The Season field do not exist'

```
API error on /fixtures/events: {'season': 'The Season field do not exist.'}
```

**Cause**

The central `api_get()` function was automatically appending `season=2022` to every request, including fixture sub-endpoints like `/fixtures/events` which do not accept a season parameter — they only need a fixture ID.

**Fix**

Created a `NO_SEASON_ENDPOINTS` set. The `api_get()` function checks this set before appending the season parameter:

```python
NO_SEASON_ENDPOINTS = {
    'fixtures/events',
    'fixtures/lineups',
    'fixtures/statistics',
    'fixtures/players'
}

def api_get(endpoint, params={}):
    if endpoint not in NO_SEASON_ENDPOINTS:
        params['season'] = SEASON
```

---

### Problem 6 — Rate limit hit when fetching events

```
{'rateLimit': 'Too many requests. You have reached your per-minute request limit. Please wait a few seconds before retrying.'}
```

**Cause**

The `fetch_all_events()` function fired one HTTP request per fixture with no delay between them. With 64 fixtures, this flooded the per-minute rate limit almost instantly.

**Fix**

- Added `time.sleep(2)` between each fixture request to stay within the per-minute cap
- Added `time.sleep(60)` as a recovery pause when a rate limit error is detected
- Commented out `fetch_all_events()` in the main block — run it separately the next day when the daily quota resets

---

## 5. Main Files and Key Functions

### test_api.py — API Connection Test

A one-off script used to verify that the API key loads correctly and the API-Football endpoint responds. Not used after Phase 1.

| **Function** | **What it does** |
|---|---|
| `test_connection()` | Calls `GET /leagues?id=1&season=2022`, checks for errors, and prints the league name, country, season year, and available data coverage |

---

### database.py — Table Definitions

Defines all six SQLAlchemy ORM models. Running this file directly calls `init_db()` which creates all tables in PostgreSQL if they do not already exist.

| **Model / Table** | **What it stores** |
|---|---|
| Team | `team_id`, `name`, `code`, `country`, `group_name`, `logo_url` |
| Match | `fixture_id`, `date`, `venue`, `city`, `status`, `elapsed`, `round`, home/away team IDs, home/away goals |
| Event | Goals, yellow cards, red cards, and substitutions — `minute`, `team`, `player`, `assist`, `type`, `detail` |
| Standing | Group table row per team — `rank`, `points`, `played`, `won`, `drawn`, `lost`, goals for/against, goal difference, `form` |
| Player | `player_id`, `name`, `nationality`, `position`, `age`, `height`, `weight`, `photo_url`, `team_id` |
| PlayerStat | Per-match player stats — `rating`, `minutes`, `goals`, `assists`, `shots`, `passes`, `tackles`, `cards` |

| **Function** | **What it does** |
|---|---|
| `init_db()` | Calls `Base.metadata.create_all(engine)` to create all six tables in the connected PostgreSQL database |

---

### fetcher.py — Data Fetching

The core data layer. Contains one central API helper and four fetch functions that pull data from the API and upsert it into the database.

| **Function** | **What it does** |
|---|---|
| `api_get()` | Central HTTP helper — builds the request, checks the errors field, prints remaining daily quota, and skips the season param for fixture sub-endpoints |
| `fetch_teams()` | Fetches all 32 teams from `GET /teams` and saves them to the teams table. Skips teams already in the database |
| `fetch_fixtures()` | Fetches all 64 fixtures from `GET /fixtures`. Saves new matches and updates status, elapsed time, and scores for existing ones |
| `fetch_standings()` | Fetches all group standings from `GET /standings`. Loops through all 8 groups and upserts each team row |
| `fetch_all_events()` | Queries the database for all finished or live matches, then fetches goals, cards, and substitutions from `GET /fixtures/events` for each — with a 2-second delay between requests |

---

### scheduler.py — Automation

Runs in the background and calls fetcher functions on a timer. Uses APScheduler's `BackgroundScheduler` so the main thread stays alive and can be stopped cleanly with Ctrl+C.

| **Function / Job** | **Schedule and purpose** |
|---|---|
| `startup()` | Runs once immediately on launch — fetches teams, fixtures, and standings to populate the database on first run |
| `regular_update()` | Runs every 10 minutes — refreshes fixtures and standings to catch score and status changes |
| `live_update()` | Runs every 15 seconds — checks if any match is currently live; only fetches events if a live match is detected |
| `is_match_live()` | Helper — queries the matches table for any row with a live status (`1H`, `2H`, `HT`, `ET`, `P`, `BT`) and returns `True` or `False` |

---

## 6. Database Schema

All tables are in the `worldcup` PostgreSQL database. The `fixture_id` and `team_id` columns are the primary foreign keys linking tables together.

```
teams
  team_id (PK) | name | code | country | group_name | logo_url

matches
  fixture_id (PK) | date | venue | city | status | elapsed
  round | home_team_id (FK) | away_team_id (FK) | home_goals | away_goals

events
  id (PK) | fixture_id (FK) | minute | extra_minute | team_id (FK)
  player_name | assist_name | event_type | detail

standings
  id (PK) | team_id (FK) | group_name | rank | points
  played | won | drawn | lost | goals_for | goals_against | goal_diff | form

players
  player_id (PK) | name | nationality | position | age
  height | weight | photo_url | team_id (FK)

player_stats
  id (PK) | fixture_id (FK) | player_id (FK) | rating | minutes_played
  goals | assists | shots_total | shots_on | passes_total | passes_key
  tackles | yellow_cards | red_cards
```

---

## 7. Environment Variables (.env)

The `.env` file stores all secrets and configuration. It is excluded from version control via `.gitignore`. Never hardcode these values in your Python files.

```
# API
API_FOOTBALL_KEY=your_api_key_here

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=worldcup
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
```

---

## 8. API-Football Notes

| **Detail** | **Value** |
|---|---|
| Base URL | `https://v3.football.api-sports.io` |
| Auth header | `x-apisports-key: YOUR_KEY` |
| World Cup league ID | `1` |
| Free tier seasons | 2022 and earlier |
| Paid tier seasons | 2026 (current tournament) |
| Daily request limit | 100 requests/day (free tier) |
| Per-minute limit | ~10 requests/minute (free tier) |
| Live data refresh rate | Every 15 seconds |
| Remaining quota header | `x-ratelimit-requests-remaining` |

### Key Endpoints Used

| **Endpoint** | **Purpose** |
|---|---|
| `GET /leagues` | Check season coverage and confirm API connection |
| `GET /teams` | Fetch all 32 participating teams |
| `GET /fixtures` | Fetch full match schedule (64 matches for 2022) |
| `GET /standings` | Fetch all group table standings |
| `GET /fixtures/events` | Fetch goals, cards, and substitutions for a fixture |
| `GET /fixtures?live=all` | Fetch all currently live matches across all leagues |

---

## 9. Next Steps — Phase 4

Phase 4 will build the Streamlit dashboard UI. The database is fully populated and the scheduler keeps it updated automatically. The UI will have six pages:

| **Page** | **What it shows** |
|---|---|
| Live Scores | Current scoreline, match minute, goals, cards, and substitutions in real time |
| Group Standings | All 8 group tables with points, goal difference, and recent form |
| Knockout Bracket | Visual bracket from Round of 16 through to the Final |
| Team Page | Squad list, coach, match history, and team statistics |
| Player Stats | Top scorers, top assists, and disciplinary leaderboard |
| Match Detail | Lineups, event timeline, and per-player ratings for any match |

To start Phase 4, run:

```bash
pip install streamlit
streamlit run dashboard.py
```
