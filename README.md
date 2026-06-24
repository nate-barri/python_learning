# python_learning
will use to learn python

<<<<<<< HEAD
# World Cup Dashboard
Day 1

**Project Documentation**

=======
World cup project
Day 1
>>>>>>> 88a24aeb0317da9312ac82727b63fe2674b9066a
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
<<<<<<< HEAD

Streamlit will open the dashboard automatically in your browser at `http://localhost:8501`.



# World Cup Dashboard
Day 2

# World Cup Dashboard

**Phase 4 — Dashboard UI Documentation**

`Streamlit` | `PostgreSQL` | `Python` | `API-Football`

| **Project** | **World Cup Sports Dashboard** |
|---|---|
| Author | Nathaniel |
| Phase | 4 — Dashboard UI |
| Framework | Streamlit |
| Database | PostgreSQL |
| Season | 2022 (free tier) / 2026 (paid) |
| Date | June 24, 2026 |

---

## 1. Phase 4 Overview

Phase 4 built the Streamlit dashboard UI on top of the database and fetcher from Phases 1–3. The dashboard is a multi-page web app running at `http://localhost:8501` with six pages navigable from the sidebar.

### Pages Built

| **Page** | **File** |
|---|---|
| Home | `dashboard.py` |
| Group Standings | `pages/1_Standings.py` |
| Match Schedule | `pages/2_Schedule.py` |
| Match Detail | `pages/3_Match_Detail.py` |
| Teams | `pages/4_Teams.py` |
| Player Stats | `pages/5_Player_Stats.py` |
| Live Scores | `pages/6_Live_Scores.py` (upcoming) |

### Shared Utilities

| **File** | **Purpose** |
|---|---|
| `utils/db.py` | All database query functions shared across every page |
| `.streamlit/config.toml` | Forces light theme — prevents Streamlit's default dark mode |

---

## 2. Final Folder Structure

```
worldcup-dashboard/
│
+-- dashboard.py              <- Home page entry point
+-- database.py              <- SQLAlchemy table definitions
+-- fetcher.py               <- All API fetch functions
+-- scheduler.py             <- APScheduler automation
+-- .env                     <- API key and DB credentials
+-- .gitignore
│
+-- pages/
│   +-- 1_Standings.py       <- Group standings page
│   +-- 2_Schedule.py        <- Match schedule page
│   +-- 3_Match_Detail.py    <- Match detail and events
│   +-- 4_Teams.py           <- Team profiles and history
│   +-- 5_Player_Stats.py    <- Player stats and deep dive
│   +-- 6_Live_Scores.py     <- Live scores (upcoming)
│
+-- utils/
│   +-- __init__.py          <- Makes utils a Python package
│   +-- db.py               <- Shared database query functions
│
+-- .streamlit/
│   +-- config.toml         <- Light theme configuration
│
+-- venv/                   <- Virtual environment
```

---

## 3. pip Installs in Phase 4

No new pip installs were required in Phase 4. All packages were already installed in Phases 1–3. For reference, the full install command remains:

```
pip install requests pandas sqlalchemy streamlit python-dotenv psycopg2-binary apscheduler
```

Streamlit was installed in Phase 1 and is launched with:

```
& .../worldcup-dashboard/venv/Scripts/streamlit.exe run .../dashboard.py
```

---

## 4. Problems Encountered and Fixes

### Problem 1 — HTML rendering as raw text on Schedule page

```html
<!-- Home team -->
<div style='flex:1; text-align:right;'>
  <span style='font-size:16px; font-weight:600;'>Qatar</span>
</div>
...
```

**Cause**

The Schedule page used a large outer `<div>` with `display:flex` to lay out three columns. Streamlit's HTML renderer does not support flexbox layouts reliably, so the raw HTML was printed as plain text instead of being rendered.

**Fix**

Replaced the flex layout with native Streamlit `st.columns()` for the three-column structure (home team | score | away team). Only small inline HTML fragments were kept for styling text — no outer layout divs.

```python
# Wrong — flexbox div rendered as raw text
st.markdown('<div style="display:flex">...</div>', unsafe_allow_html=True)

# Correct — native Streamlit columns
col_home, col_score, col_away = st.columns([3, 2, 3])
with col_home:
    st.markdown('<p style="text-align:right;">Qatar</p>', unsafe_allow_html=True)
```

---

### Problem 2 — Streamlit dark theme overriding custom styles

```
Blue highlighted text on white background.
All text rendered with dark theme colors despite CSS overrides.
```

**Cause**

Streamlit defaults to a dark theme based on system settings. Custom CSS in `st.markdown()` cannot override the base theme because theme colors are applied at a higher level.

**Fix**

Created a `.streamlit/config.toml` file in the project root to force the light theme at the application level:

```toml
[theme]
base = "light"
primaryColor = "#1F4E79"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F8F9FA"
textColor = "#1A1A1A"
font = "sans serif"
```

**How to create the file on Windows**

```powershell
mkdir .../worldcup-dashboard/.streamlit
New-Item .../worldcup-dashboard/.streamlit/config.toml -ItemType File
notepad .../worldcup-dashboard/.streamlit/config.toml
```

---

### Problem 3 — Running dashboard with python.exe instead of streamlit.exe

```
Warning: to view this Streamlit app on a browser, run it with the following command:
  streamlit run dashboard.py [ARGUMENTS]
Thread 'MainThread': missing ScriptRunContext! (repeated many times)
```

**Cause**

The dashboard was launched using `python.exe dashboard.py` instead of `streamlit.exe run dashboard.py`. Streamlit apps must be launched through the `streamlit` command — running with Python directly skips the Streamlit server entirely.

**Fix**

```bash
# Wrong
& .../venv/Scripts/python.exe dashboard.py

# Correct
& .../venv/Scripts/streamlit.exe run dashboard.py
```

---

### Problem 4 — Round filter showing wrong order on Schedule page

```
All / 3rd Place Final / Final / Group Stage - 1 / Group Stage - 2 / ...
(alphabetical order instead of chronological)
```

**Cause**

Rounds were sorted alphabetically from the database, so `3rd Place Final` and `Final` appeared before `Group Stage` rounds.

**Fix**

Defined a manual `ROUND_ORDER` list and sorted rounds against it using `list.index()`:

```python
ROUND_ORDER = [
    'Group Stage - 1', 'Group Stage - 2', 'Group Stage - 3',
    'Round of 16', 'Quarter-finals', 'Semi-finals',
    '3rd Place Final', 'Final'
]

sorted_rounds = sorted(all_rounds, key=lambda r: ROUND_ORDER.index(r)
                       if r in ROUND_ORDER else 99)
```

---

### Problem 5 — pandas DatabaseError: can't adapt type numpy.int64

```
pandas.errors.DatabaseError: Execution failed on sql
[parameters: {'tid': np.int64(2382)}]
psycopg2.ProgrammingError: can't adapt type 'numpy.int64'
```

**Cause**

The `team_id` value was read from a pandas DataFrame which stores integers as `numpy.int64`. PostgreSQL's psycopg2 driver only accepts plain Python `int` types as query parameters, not numpy integer types.

**Fix**

Added `int()` conversion at the start of any function that receives an ID from a DataFrame:

```python
def get_team_detail(team_id):
    team_id = int(team_id)  # convert numpy.int64 to plain Python int
    query = text("""SELECT ... WHERE m.home_team_id = :tid""")
```

---

### Problem 6 — Daily API quota drained by scheduler running every 10 minutes

```
API error: 'You have reached the request limit for the day.'
Requests remaining: 0
```

**Cause**

The scheduler was running `regular_update()` every 10 minutes, which calls `fetch_fixtures()` and `fetch_standings()` — 2 requests per run. Over 24 hours that is 288 requests, far exceeding the 100/day free tier limit. Additionally, `startup()` fetched teams, fixtures, and standings every time the scheduler started, even when the database was already populated.

**Fix**

- **Changed `regular_update()` interval** from 10 minutes to 60 minutes — reduces to 48 requests/day
- **Rewrote `startup()`** to check if data exists first — only fetches if tables are empty

```python
def startup():
    session = Session()
    team_count  = session.query(Team).count()
    match_count = session.query(Match).count()
    session.close()

    if team_count == 0:
        fetch_teams()
    else:
        log.info(f'Teams already loaded ({team_count}) — skipping.')

    if match_count == 0:
        fetch_fixtures()
        fetch_standings()
    else:
        log.info(f'Fixtures already loaded ({match_count}) — skipping.')
```

---

## 5. Main Files and Key Functions

### utils/db.py — Shared Database Queries

Central query file imported by every page. All functions return pandas DataFrames. Avoids duplicating SQL across pages.

| **Function** | **What it does** |
|---|---|
| `get_standings()` | Returns all group standings joined with team names, ordered by group and rank |
| `get_fixtures(round_name)` | Returns all fixtures or filters by round. Joins home and away team names |
| `get_rounds()` | Returns a sorted list of all distinct round names from the matches table |
| `get_match_detail(fixture_id)` | Returns match info and all events for a single fixture as two DataFrames |
| `get_teams()` | Returns all 32 teams with `team_id`, `name`, `country`, `logo_url` |
| `get_team_detail(team_id)` | Returns all finished matches for a team with W/D/L result calculated via SQL CASE |
| `get_top_scorers()` | Counts goals per player from events table, excludes own goals and missed penalties |
| `get_top_assists()` | Counts assists per player from events table where `assist_name` is not null |
| `get_top_cards()` | Counts yellow and red cards per player using `COUNT(*) FILTER` |
| `get_tournament_player_stats()` | Aggregates `player_stats` across all matches with computed metrics: shot accuracy, conversion rate, goals per 90, assists per 90 |
| `get_player_deep_dive(name)` | Returns per-match stats for a single named player ordered by date |
| `get_all_player_names()` | Returns list of all player names who have recorded stats |

---

### dashboard.py — Home Page

Main entry point. Sets the page config, injects global CSS for the light theme, and displays the home page with 4 stat cards and navigation instructions.

| **Element** | **What it shows** |
|---|---|
| 4 stat cards | 32 Teams, 64 Matches, 8 Groups, Qatar (host country) |
| Navigation list | Links to each page with a short description |
| Global CSS | Card styles, badge colors, and hides the default Streamlit menu and footer |

---

### pages/1_Standings.py — Group Standings

Displays all 8 group tables in a 2-column grid. Each table has a header row, team rows with a green left border for the top 2 qualifiers, and a form guide below.

| **Feature** | **Detail** |
|---|---|
| Layout | Two groups per row using `st.columns(2)` |
| Qualification bar | Green left border on rank 1 and 2 rows — indicates promotion to Round of 16 |
| Form badges | W/D/L colored pills rendered with inline HTML for each team's recent form string |
| Columns shown | Rank, Team, P, W, D, L, GF, GA, GD, Pts |

---

### pages/2_Schedule.py — Match Schedule

Lists all 64 fixtures with a round filter at the top. Group stage matches show 2 per row; knockout matches show 1 centred.

| **Feature** | **Detail** |
|---|---|
| Round filter | Horizontal radio buttons in correct chronological order — All, Group Stage 1–3, Round of 16, Quarter-finals, Semi-finals, 3rd Place Final, Final |
| Summary metrics | Total matches, Played, Upcoming, Live Now — shown as `st.metric()` cards |
| Match card | Home team │ score │ away team in 3 columns with status (FT/LIVE/HT/Upcoming) and venue below |
| Grid layout | Group stages: 2 matches per row. Knockouts: 1 match centred in a 1-2-1 column layout |

---

### pages/3_Match_Detail.py — Match Detail

Two dropdowns let the user pick a round then a match. Shows a large score header and a split events timeline.

| **Feature** | **Detail** |
|---|---|
| Match selector | Round dropdown filters the match dropdown — match labels show score for finished games |
| Score header | Large score in a grey card with round, date, venue below |
| Events timeline | Home events on the left, away events on the right, separated by a vertical divider line |
| Event icons | Goal = soccer ball, Yellow Card = yellow square, Red Card = red square, Substitution = arrows |
| Event summary | 3 metrics at the bottom: total goals, cards, and substitutions |

---

### pages/4_Teams.py — Teams

Sidebar dropdown to select any team. Shows group standing stats and a full match history with results.

| **Feature** | **Detail** |
|---|---|
| Team selector | Teams sorted alphabetically within groups in the sidebar |
| Header stats | 5 metrics: Points, Won, Drawn, Lost, Goal Difference from standings table |
| Match history | All finished matches with date, round, score, opponent. Selected team name bolded |
| Result badges | W = green, D = amber, L = red colored pills |
| Tournament summary | 6 metrics at bottom: Played, Wins, Draws, Losses, Goals Scored, Goals Conceded |

---

### pages/5_Player_Stats.py — Player Stats

Four tabs covering tournament-wide stats, team/group filters, and a per-player deep dive.

| **Tab** | **What it shows** |
|---|---|
| Top Scorers & Assists | Ranked leaderboards with medal icons for top 3 and progress bars. Sub-tabs for scorers, assists, and disciplinary table |
| Tournament Stats | Full player table with category switcher: Attacking, Passing, Defending, Discipline, Per 90. Powered by `get_tournament_player_stats()` |
| By Team / Group | Same stats table filtered to one team or one group stage. Useful for intra-group comparisons |
| Player Deep Dive | Select any player — shows overview metrics, attacking/passing/defending/discipline sections, and a match-by-match breakdown with ratings color coded green/amber/red |

#### Computed Metrics in Player Stats

| **Metric** | **Formula** |
|---|---|
| Shot Accuracy % | Shots on Target / Total Shots × 100 |
| Conversion Rate % | Goals / Total Shots × 100 |
| Goals per 90 | Goals / Minutes × 90 |
| Assists per 90 | Assists / Minutes × 90 |
| Goal Involvements | Goals + Assists |
| Avg Rating | AVG(rating) across all matches played |

---

## 6. New Fetcher Function Added in Phase 4

### fetch_player_stats() — Added to fetcher.py

Fetches per-match player statistics from `GET /fixtures/players` for every finished match. Saves data to both the `players` and `player_stats` tables. Required to power the Tournament Stats, By Team/Group, and Player Deep Dive tabs.

| **Detail** | **Value** |
|---|---|
| Endpoint | `GET /fixtures/players?fixture=FIXTURE_ID` |
| Data saved | `rating`, `minutes_played`, `goals`, `assists`, `shots_total`, `shots_on`, `passes_total`, `passes_key`, `tackles`, `yellow_cards`, `red_cards` |
| Rate limiting | `time.sleep(2)` between each fixture — same pattern as `fetch_all_events()` |
| Requests used | 1 per finished match — 64 requests for the full 2022 tournament |
| When to run | Run on a day when `fetch_all_events()` has NOT been run — combined they exceed the 100/day free tier limit |

```python
# Add to fetcher.py — run the day after fetch_all_events()
if __name__ == '__main__':
    # fetch_teams()       # skip — already in DB
    # fetch_fixtures()    # skip — already in DB
    # fetch_standings()   # skip — already in DB
    # fetch_all_events()  # run this on Day 1
    fetch_player_stats()  # run this on Day 2
```

---

## 7. Scheduler Changes in Phase 4

Two changes were made to `scheduler.py` to prevent the daily API quota from being drained by automated background jobs.

| **Change** | **Old behaviour** | **New behaviour** |
|---|---|---|
| `regular_update()` interval | Every 10 minutes = 288 req/day | Every 60 minutes = 48 req/day |
| `startup()` behaviour | Always fetched teams, fixtures, standings | Checks row counts first — only fetches if tables are empty |

### Daily Request Budget (after fix)

| **Activity** | **Requests/day** |
|---|---|
| Startup (data exists) | 0 |
| `regular_update` × 24 | 48 (2 per hour) |
| `live_update` | 0 (skips when no live matches) |
| Buffer for manual runs | 52 |
| **Total** | **48 / 100** |

---

## 8. Next Steps

| **Task** | **Detail** |
|---|---|
| Run `fetch_all_events()` | Uncomment in `fetcher.py` and run first thing tomorrow — uses 64 requests |
| Run `fetch_player_stats()` | Run the day after events — uses 64 requests. Unlocks Tabs 2, 3, and 4 on Player Stats page |
| Build Page 6 — Live Scores | Real-time score updates for any currently live World Cup matches |
| Upgrade API plan | Switch season from `2022` to `2026` to get current tournament data |
| Improve Schedule page | Add click-through from a match card to the Match Detail page |
| Add player photos | `photo_url` is stored in the players table but not yet displayed |
=======
>>>>>>> 88a24aeb0317da9312ac82727b63fe2674b9066a
