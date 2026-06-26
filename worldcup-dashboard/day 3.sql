SELECT COUNT(*) FROM events;

-- Check goals
SELECT player_name, team_id, minute, detail 
FROM events 
WHERE event_type = 'Goal' 
LIMIT 10;

-- Check the breakdown by type
SELECT event_type, COUNT(*) 
FROM events 
GROUP BY event_type;

SELECT p.name, p.team_id, t.name AS team
FROM players p
LEFT JOIN teams t ON p.team_id = t.team_id
LIMIT 10;

-- Populate team_id for each player based on which team they played for
UPDATE players p
SET team_id = subq.team_id
FROM (
    SELECT DISTINCT ON (ps.player_id)
        ps.player_id,
        CASE
            WHEN m.home_team_id IN (
                SELECT team_id FROM teams
            ) THEN m.home_team_id
            ELSE m.away_team_id
        END AS team_id
    FROM player_stats ps
    JOIN matches m ON ps.fixture_id = m.fixture_id
    ORDER BY ps.player_id, m.date
) subq
WHERE p.player_id = subq.player_id;



-- Clear existing player stats and players so they re-save with correct team_id
TRUNCATE TABLE player_stats;
TRUNCATE TABLE players CASCADE;


-- Check team_id is now populated
SELECT p.name, t.name AS team
FROM players p
JOIN teams t ON p.team_id = t.team_id
LIMIT 10;

-- Check Valencia only shows for Ecuador
SELECT player, team 
FROM (
    SELECT p.name AS player, t.name AS team
    FROM players p
    JOIN teams t ON p.team_id = t.team_id
    WHERE p.name ILIKE '%Valencia%'
) x;


SELECT COUNT(*) FROM player_stats;
SELECT COUNT(DISTINCT fixture_id) FROM player_stats;

-- See how many matches Kylian Mbappé has stats for
SELECT ps.fixture_id, ps.goals, ps.assists, ps.minutes_played
FROM player_stats ps
JOIN players p ON ps.player_id = p.player_id
WHERE p.name = 'Kylian Mbappé';



-- 1. Should return 64
SELECT COUNT(DISTINCT fixture_id) FROM player_stats;

-- 2. Should return a number close to 1400+ (roughly 22 players x 64 matches)
SELECT COUNT(*) FROM player_stats;

-- 3. Check Mbappe now has multiple matches
SELECT ps.fixture_id, ps.goals, ps.assists, ps.minutes_played, ps.rating
FROM player_stats ps
JOIN players p ON ps.player_id = p.player_id
WHERE p.name = 'Kylian Mbappé'
ORDER BY ps.fixture_id;

-- 4. Check Valencia only shows Ecuador (not Qatar)
SELECT p.name, t.name AS team
FROM players p
JOIN teams t ON p.team_id = t.team_id
WHERE p.name ILIKE '%Valencia%';