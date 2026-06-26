import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DB_URL, echo=False)


def get_standings():
    """Return all group standings ordered by group and rank."""
    query = text("""
        SELECT
            s.group_name,
            s.rank,
            t.name        AS team,
            t.logo_url,
            s.played,
            s.won,
            s.drawn,
            s.lost,
            s.goals_for,
            s.goals_against,
            s.goal_diff,
            s.points,
            s.form
        FROM standings s
        JOIN teams t ON s.team_id = t.team_id
        ORDER BY s.group_name, s.rank
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_fixtures(round_name=None):
    """Return all fixtures, optionally filtered by round."""
    where = "WHERE m.round = :round" if round_name else ""
    query = text(f"""
        SELECT
            m.fixture_id,
            m.date,
            m.round,
            m.venue,
            m.city,
            m.status,
            m.elapsed,
            m.home_goals,
            m.away_goals,
            ht.name     AS home_team,
            ht.logo_url AS home_logo,
            at.name     AS away_team,
            at.logo_url AS away_logo
        FROM matches m
        JOIN teams ht ON m.home_team_id = ht.team_id
        JOIN teams at ON m.away_team_id = at.team_id
        {where}
        ORDER BY m.date
    """)
    params = {"round": round_name} if round_name else {}
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)


def get_rounds():
    """Return a sorted list of all distinct rounds."""
    query = text("SELECT DISTINCT round FROM matches ORDER BY round")
    with engine.connect() as conn:
        result = conn.execute(query)
        return [row[0] for row in result]


def get_match_detail(fixture_id):
    """Return match info and all events for a single fixture."""
    match_query = text("""
        SELECT
            m.fixture_id,
            m.date,
            m.round,
            m.venue,
            m.city,
            m.status,
            m.elapsed,
            m.home_goals,
            m.away_goals,
            ht.name     AS home_team,
            ht.logo_url AS home_logo,
            at.name     AS away_team,
            at.logo_url AS away_logo
        FROM matches m
        JOIN teams ht ON m.home_team_id = ht.team_id
        JOIN teams at ON m.away_team_id = at.team_id
        WHERE m.fixture_id = :fid
    """)
    events_query = text("""
        SELECT
            e.minute,
            e.extra_minute,
            e.event_type,
            e.detail,
            e.player_name,
            e.assist_name,
            t.name AS team
        FROM events e
        JOIN teams t ON e.team_id = t.team_id
        WHERE e.fixture_id = :fid
        ORDER BY e.minute
    """)
    with engine.connect() as conn:
        match = pd.read_sql(match_query, conn, params={"fid": fixture_id})
        events = pd.read_sql(events_query, conn, params={"fid": fixture_id})
    return match, events


def get_teams():
    """Return all teams."""
    query = text("SELECT team_id, name, country, logo_url FROM teams ORDER BY name")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_team_detail(team_id):
    """Return all matches for a specific team."""
    team_id = int(team_id)  # convert numpy.int64 to plain Python int
    query = text("""
        SELECT
            m.fixture_id,
            m.date,
            m.round,
            m.status,
            m.home_goals,
            m.away_goals,
            ht.name AS home_team,
            at.name AS away_team,
            CASE
                WHEN m.home_team_id = :tid AND m.home_goals > m.away_goals  THEN 'W'
                WHEN m.away_team_id = :tid AND m.away_goals > m.home_goals  THEN 'W'
                WHEN m.home_goals = m.away_goals                            THEN 'D'
                ELSE 'L'
            END AS result
        FROM matches m
        JOIN teams ht ON m.home_team_id = ht.team_id
        JOIN teams at ON m.away_team_id = at.team_id
        WHERE (m.home_team_id = :tid OR m.away_team_id = :tid)
          AND m.status = 'FT'
        ORDER BY m.date
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={"tid": team_id})


def get_top_scorers():
    """Return players with the most goals from player_stats — covers all 64 matches."""
    query = text("""
        SELECT
            p.name        AS player_name,
            t.name        AS team,
            SUM(ps.goals) AS goals
        FROM player_stats ps
        JOIN players p ON ps.player_id = p.player_id
        JOIN teams t   ON p.team_id    = t.team_id
        GROUP BY p.name, t.name
        HAVING SUM(ps.goals) > 0
        ORDER BY goals DESC
        LIMIT 20
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_top_assists():
    """Return players with the most assists from player_stats — covers all 64 matches."""
    query = text("""
        SELECT
            p.name           AS player_name,
            t.name           AS team,
            SUM(ps.assists)  AS assists
        FROM player_stats ps
        JOIN players p ON ps.player_id = p.player_id
        JOIN teams t   ON p.team_id    = t.team_id
        GROUP BY p.name, t.name
        HAVING SUM(ps.assists) > 0
        ORDER BY assists DESC
        LIMIT 20
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_top_cards():
    """Return players with the most cards from player_stats — covers all 64 matches."""
    query = text("""
        SELECT
            p.name               AS player_name,
            t.name               AS team,
            SUM(ps.yellow_cards) AS yellow_cards,
            SUM(ps.red_cards)    AS red_cards
        FROM player_stats ps
        JOIN players p ON ps.player_id = p.player_id
        JOIN teams t   ON p.team_id    = t.team_id
        GROUP BY p.name, t.name
        HAVING SUM(ps.yellow_cards) + SUM(ps.red_cards) > 0
        ORDER BY yellow_cards DESC, red_cards DESC
        LIMIT 20
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_live_matches():
    """Return any currently live matches."""
    query = text("""
        SELECT
            m.fixture_id,
            m.elapsed,
            m.status,
            m.home_goals,
            m.away_goals,
            ht.name     AS home_team,
            at.name     AS away_team
        FROM matches m
        JOIN teams ht ON m.home_team_id = ht.team_id
        JOIN teams at ON m.away_team_id = at.team_id
        WHERE m.status IN ('1H', '2H', 'HT', 'ET', 'P', 'BT')
        ORDER BY m.date
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_tournament_player_stats(team_name=None, group_name=None):
    """Return aggregated player stats for the tournament, optionally filtered by team or group."""
    where_clauses = ["ps.minutes_played > 0"]
    if team_name:
        where_clauses.append("t.name = :team_name")
    if group_name:
        where_clauses.append("s.group_name = :group_name")
    where = "WHERE " + " AND ".join(where_clauses)

    query = text(f"""
        SELECT
            p.name                            AS player,
            t.name                            AS team,
            s.group_name                      AS grp,
            COUNT(DISTINCT ps.fixture_id)     AS matches,
            SUM(ps.minutes_played)            AS minutes,
            SUM(ps.goals)                     AS goals,
            SUM(ps.assists)                   AS assists,
            SUM(ps.goals) + SUM(ps.assists)   AS goal_involvements,
            SUM(ps.shots_total)               AS shots,
            SUM(ps.shots_on)                  AS shots_on_target,
            CASE WHEN SUM(ps.shots_total) > 0
                 THEN ROUND(SUM(ps.shots_on)::numeric / SUM(ps.shots_total) * 100, 1)
                 ELSE 0 END                   AS shot_accuracy,
            CASE WHEN SUM(ps.shots_total) > 0
                 THEN ROUND(SUM(ps.goals)::numeric / SUM(ps.shots_total) * 100, 1)
                 ELSE 0 END                   AS conversion_rate,
            SUM(ps.passes_total)              AS passes,
            SUM(ps.passes_key)                AS key_passes,
            SUM(ps.tackles)                   AS tackles,
            SUM(ps.yellow_cards)              AS yellow_cards,
            SUM(ps.red_cards)                 AS red_cards,
            ROUND(AVG(ps.rating)::numeric, 2) AS avg_rating,
            CASE WHEN SUM(ps.minutes_played) > 0
                 THEN ROUND(SUM(ps.goals)::numeric   / SUM(ps.minutes_played) * 90, 2)
                 ELSE 0 END                   AS goals_per_90,
            CASE WHEN SUM(ps.minutes_played) > 0
                 THEN ROUND(SUM(ps.assists)::numeric / SUM(ps.minutes_played) * 90, 2)
                 ELSE 0 END                   AS assists_per_90
        FROM player_stats ps
        JOIN players p   ON ps.player_id  = p.player_id
        JOIN matches m   ON ps.fixture_id = m.fixture_id
        JOIN teams t     ON p.team_id     = t.team_id
        JOIN standings s ON t.team_id     = s.team_id
        {where}
        GROUP BY p.name, t.name, s.group_name
        ORDER BY goal_involvements DESC, avg_rating DESC
    """)
    params = {}
    if team_name:
        params["team_name"] = team_name
    if group_name:
        params["group_name"] = group_name
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)


def get_player_deep_dive(player_name):
    """Return per-match stats for a single player."""
    query = text("""
        SELECT
            m.date,
            m.round,
            ht.name     AS home_team,
            at.name     AS away_team,
            m.home_goals,
            m.away_goals,
            ps.minutes_played,
            ps.rating,
            ps.goals,
            ps.assists,
            ps.shots_total,
            ps.shots_on,
            ps.passes_total,
            ps.passes_key,
            ps.tackles,
            ps.yellow_cards,
            ps.red_cards
        FROM player_stats ps
        JOIN players p  ON ps.player_id  = p.player_id
        JOIN matches m  ON ps.fixture_id = m.fixture_id
        JOIN teams ht   ON m.home_team_id = ht.team_id
        JOIN teams at   ON m.away_team_id = at.team_id
        WHERE p.name = :player_name
          AND ps.minutes_played > 0
        ORDER BY m.date
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={"player_name": player_name})


def get_all_player_names():
    """Return all players who have stats recorded."""
    query = text("""
        SELECT DISTINCT p.name
        FROM players p
        JOIN player_stats ps ON p.player_id = ps.player_id
        WHERE ps.minutes_played > 0
        ORDER BY p.name
    """)
    with engine.connect() as conn:
        result = conn.execute(query)
        return [row[0] for row in result]


def get_players_by_team(team_name):
    """Return all player names for a specific team who have stats."""
    query = text("""
        SELECT DISTINCT p.name
        FROM players p
        JOIN teams t    ON p.team_id    = t.team_id
        JOIN player_stats ps ON p.player_id = ps.player_id
        WHERE t.name = :team_name
          AND ps.minutes_played > 0
        ORDER BY p.name
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"team_name": team_name})
        return [row[0] for row in result]


def get_top_assist_providers():
    """Return players with most goal assists — passes that directly led to goals."""
    query = text("""
        SELECT
            TRIM(e.assist_name)  AS player_name,
            t.name               AS team,
            COUNT(*)             AS goal_assists
        FROM events e
        JOIN teams t ON e.team_id = t.team_id
        WHERE e.event_type = 'Goal'
          AND e.detail NOT IN ('Own Goal', 'Missed Penalty')
          AND e.assist_name IS NOT NULL
          AND TRIM(e.assist_name) != ''
        GROUP BY TRIM(e.assist_name), t.name
        ORDER BY goal_assists DESC
        LIMIT 20
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)