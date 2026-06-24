# World Cup Dashboard — Data Dictionary

**Database:** `worldcup` (PostgreSQL)  
**ORM:** SQLAlchemy  
**Source:** API-Football (api-sports.io) — League ID `1`, Season `2022`

---

## Tables Overview

| **Table** | **Description** | **Rows (2022)** |
|---|---|---|
| `teams` | All participating teams | 32 |
| `matches` | Full fixture list with scores and status | 64 |
| `events` | Goals, cards, and substitutions per match | ~600 |
| `standings` | Group table row per team | 32 |
| `players` | Player profiles | ~800 |
| `player_stats` | Per-match player performance stats | ~5,000 |

---

## teams

Populated by `fetch_teams()` via `GET /teams`. One row per participating nation.

| **Column** | **Type** | **Key** | **Description** |
|---|---|---|---|
| `team_id` | `INTEGER` | PK | Unique team identifier from API-Football |
| `name` | `VARCHAR` | | Full team name (e.g. `Brazil`) |
| `code` | `VARCHAR(3)` | | 3-letter team code (e.g. `BRA`) |
| `country` | `VARCHAR` | | Country name — matches `name` for national teams |
| `group_name` | `VARCHAR` | | World Cup group (e.g. `Group A`) |
| `logo_url` | `VARCHAR` | | URL to team badge image (stored, not yet displayed in UI) |

---

## matches

Populated by `fetch_fixtures()` via `GET /fixtures`. One row per scheduled or completed match. Updated on each `regular_update()` run to refresh score, status, and elapsed time.

| **Column** | **Type** | **Key** | **Description** |
|---|---|---|---|
| `fixture_id` | `INTEGER` | PK | Unique match identifier from API-Football |
| `date` | `TIMESTAMP` | | Scheduled kick-off date and time (UTC) |
| `venue` | `VARCHAR` | | Stadium name (e.g. `Lusail Iconic Stadium`) |
| `city` | `VARCHAR` | | Host city (e.g. `Lusail`) |
| `status` | `VARCHAR` | | Match status code — see status codes table below |
| `elapsed` | `INTEGER` | | Current match minute — `NULL` if not started or finished |
| `round` | `VARCHAR` | | Tournament round (e.g. `Group Stage - 1`, `Final`) |
| `home_team_id` | `INTEGER` | FK → `teams.team_id` | Home team reference |
| `away_team_id` | `INTEGER` | FK → `teams.team_id` | Away team reference |
| `home_goals` | `INTEGER` | | Home team full-time goals — `NULL` if not yet played |
| `away_goals` | `INTEGER` | | Away team full-time goals — `NULL` if not yet played |

**Status codes**

| **Code** | **Meaning** |
|---|---|
| `NS` | Not Started |
| `1H` | First Half — Live |
| `HT` | Half Time — Live |
| `2H` | Second Half — Live |
| `ET` | Extra Time — Live |
| `BT` | Break (between extra time halves) — Live |
| `P` | Penalty Shootout — Live |
| `FT` | Full Time — Finished |
| `AET` | After Extra Time — Finished |
| `PEN` | After Penalties — Finished |

**Round values**

`Group Stage - 1`, `Group Stage - 2`, `Group Stage - 3`, `Round of 16`, `Quarter-finals`, `Semi-finals`, `3rd Place Final`, `Final`

---

## events

Populated by `fetch_all_events()` via `GET /fixtures/events`. One row per in-match event (goal, card, substitution). Requires a separate daily run due to rate limits — 64 API requests for the full tournament.

| **Column** | **Type** | **Key** | **Description** |
|---|---|---|---|
| `id` | `INTEGER` | PK | Auto-generated surrogate key |
| `fixture_id` | `INTEGER` | FK → `matches.fixture_id` | The match this event belongs to |
| `minute` | `INTEGER` | | Match minute the event occurred |
| `extra_minute` | `INTEGER` | | Added time minute — `NULL` if not in added time |
| `team_id` | `INTEGER` | FK → `teams.team_id` | Team the event is attributed to |
| `player_name` | `VARCHAR` | | Name of the primary player involved |
| `assist_name` | `VARCHAR` | | Assisting player for goals — `NULL` for cards and substitutions |
| `event_type` | `VARCHAR` | | High-level event category — see event types below |
| `detail` | `VARCHAR` | | Sub-type detail — see detail values below |

**Event types and detail values**

| **event_type** | **detail values** |
|---|---|
| `Goal` | `Normal Goal`, `Own Goal`, `Penalty`, `Missed Penalty` |
| `Card` | `Yellow Card`, `Red Card`, `Yellow Card Second` |
| `subst` | `Substitution 1` through `Substitution N` |

> `get_top_scorers()` excludes `Own Goal` and `Missed Penalty` from its count. `get_top_assists()` only counts rows where `assist_name IS NOT NULL`.

---

## standings

Populated by `fetch_standings()` via `GET /standings`. One row per team representing their position in the group table. Updated on each `regular_update()` run.

| **Column** | **Type** | **Key** | **Description** |
|---|---|---|---|
| `id` | `INTEGER` | PK | Auto-generated surrogate key |
| `team_id` | `INTEGER` | FK → `teams.team_id` | Team reference |
| `group_name` | `VARCHAR` | | Group identifier (e.g. `Group A`) — matches `teams.group_name` |
| `rank` | `INTEGER` | | Current position within the group (1–4) |
| `points` | `INTEGER` | | Accumulated points (W=3, D=1, L=0) |
| `played` | `INTEGER` | | Matches played |
| `won` | `INTEGER` | | Matches won |
| `drawn` | `INTEGER` | | Matches drawn |
| `lost` | `INTEGER` | | Matches lost |
| `goals_for` | `INTEGER` | | Total goals scored |
| `goals_against` | `INTEGER` | | Total goals conceded |
| `goal_diff` | `INTEGER` | | Goal difference (`goals_for - goals_against`) |
| `form` | `VARCHAR` | | Recent match results string (e.g. `WWDL`) — `W`, `D`, or `L` per match |

---

## players

Populated by `fetch_player_stats()` via `GET /fixtures/players`. One row per player profile. `team_id` links each player to their squad.

| **Column** | **Type** | **Key** | **Description** |
|---|---|---|---|
| `player_id` | `INTEGER` | PK | Unique player identifier from API-Football |
| `name` | `VARCHAR` | | Full player name |
| `nationality` | `VARCHAR` | | Player's nationality |
| `position` | `VARCHAR` | | Playing position — `Goalkeeper`, `Defender`, `Midfielder`, `Attacker` |
| `age` | `INTEGER` | | Player age at time of tournament |
| `height` | `VARCHAR` | | Height in cm (stored as string, e.g. `185 cm`) |
| `weight` | `VARCHAR` | | Weight in kg (stored as string, e.g. `80 kg`) |
| `photo_url` | `VARCHAR` | | URL to player headshot — stored but not yet displayed in UI |
| `team_id` | `INTEGER` | FK → `teams.team_id` | Squad the player belongs to |

---

## player_stats

Populated by `fetch_player_stats()` via `GET /fixtures/players`. One row per player per match played. Requires a separate daily run — 64 API requests for the full tournament. Powers Tabs 2, 3, and 4 on the Player Stats page.

| **Column** | **Type** | **Key** | **Description** |
|---|---|---|---|
| `id` | `INTEGER` | PK | Auto-generated surrogate key |
| `fixture_id` | `INTEGER` | FK → `matches.fixture_id` | The match these stats are from |
| `player_id` | `INTEGER` | FK → `players.player_id` | The player these stats belong to |
| `rating` | `FLOAT` | | Match performance rating (0.0–10.0, API-Football scale) |
| `minutes_played` | `INTEGER` | | Minutes on the pitch in this match |
| `goals` | `INTEGER` | | Goals scored in this match |
| `assists` | `INTEGER` | | Assists in this match |
| `shots_total` | `INTEGER` | | Total shots attempted |
| `shots_on` | `INTEGER` | | Shots on target |
| `passes_total` | `INTEGER` | | Total passes attempted |
| `passes_key` | `INTEGER` | | Key passes (leading to a shot) |
| `tackles` | `INTEGER` | | Tackles made |
| `yellow_cards` | `INTEGER` | | Yellow cards received (0 or 1 per match) |
| `red_cards` | `INTEGER` | | Red cards received (0 or 1 per match) |

**Computed metrics derived from this table (not stored)**

| **Metric** | **Formula** | **Used in** |
|---|---|---|
| Shot Accuracy % | `shots_on / shots_total × 100` | Tournament Stats, Player Deep Dive |
| Conversion Rate % | `goals / shots_total × 100` | Tournament Stats, Player Deep Dive |
| Goals per 90 | `goals / minutes_played × 90` | Per 90 tab |
| Assists per 90 | `assists / minutes_played × 90` | Per 90 tab |
| Goal Involvements | `goals + assists` | Top Scorers & Assists tab |
| Avg Rating | `AVG(rating)` across all matches | Player Deep Dive |

---

## Entity Relationship Diagram

```
teams
  team_id (PK)
    │
    ├──── matches.home_team_id (FK)
    ├──── matches.away_team_id (FK)
    ├──── events.team_id (FK)
    ├──── standings.team_id (FK)
    └──── players.team_id (FK)

matches
  fixture_id (PK)
    │
    ├──── events.fixture_id (FK)
    └──── player_stats.fixture_id (FK)

players
  player_id (PK)
    │
    └──── player_stats.player_id (FK)
```

---

## Data Load Order

Tables must be populated in this order to satisfy foreign key constraints.

| **Step** | **Table(s)** | **Function** | **API requests** |
|---|---|---|---|
| 1 | `teams` | `fetch_teams()` | 1 |
| 2 | `matches` | `fetch_fixtures()` | 1 |
| 3 | `standings` | `fetch_standings()` | 8 (one per group) |
| 4 | `events` | `fetch_all_events()` | 64 (one per fixture) |
| 5 | `players`, `player_stats` | `fetch_player_stats()` | 64 (one per fixture) |

> Steps 4 and 5 each consume 64 of the 100 daily free-tier requests. **Run them on separate days.**
