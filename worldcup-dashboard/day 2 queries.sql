select players from teams;

select*from standings;

select*from teams;

select*from players
select*from player_stats
select*from public.events
select*from events;
-- Check fixtures
SELECT fixture_id, date, round, home_team_id, away_team_id, status
FROM matches
LIMIT 10;

-- Check standings
SELECT team_id, group_name, rank, points, played, won, drawn, lost
FROM standings
ORDER BY group_name, rank;

-- check standing with team names
SELECT
    s.team_id,
    t.name AS team_name,
    s.group_name,
    s.rank,
    s.points,
    s.played,
    s.won,
    s.drawn,
    s.lost
FROM standings s
JOIN teams t
    ON s.team_id = t.team_id
ORDER BY s.group_name, s.rank;

-- next query i want is to determine who moves on to the next stage
-- condition is only the top 2 teams per group name by points moves on
SELECT
    s.team_id,
    t.name AS team_name,
    s.group_name,
    s.rank,
    s.points,
    s.played,
    s.won,
    s.drawn,
    s.lost
FROM standings s
JOIN teams t
    ON s.team_id = t.team_id
	WHERE s.rank<=2
ORDER BY s.group_name, s.rank;



-- All goals from the tournament it is null fix why?
SELECT e.minute, e.extra_minute, e.player_name, e.assist_name,
       e.detail, t.name AS team
FROM events e
JOIN teams t ON e.team_id = t.team_id
WHERE e.event_type = 'Goal'
ORDER BY e.fixture_id, e.minute;