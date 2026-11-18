-- This script is now covered by createSeasonSchedule.py and makePlayoffMatches.py
-- The script remains here for posterity and future backfills of series_to_match_parent.
-- Update the parentGroupId before running.
WITH m2m AS (
  SELECT
    m.id AS sprocket_match,
    mp.id AS sprocket_match_parent,
    sf.id AS sprocket_fixture,
    f.id AS mledb_fixture,
    s.id AS mledb_series
  FROM
    sprocket."match" m
    INNER JOIN sprocket.game_mode gm ON gm.id = m."gameModeId"
    INNER JOIN sprocket.match_parent mp ON mp.id = m."matchParentId"
    INNER JOIN sprocket.schedule_fixture sf ON sf.id = mp."fixtureId"
    INNER JOIN mledb_bridge.fixture_to_fixture ftf ON ftf."sprocketFixtureId" = sf.id
    INNER JOIN mledb.fixture f ON f.id = ftf."mleFixtureId"
    INNER JOIN mledb_bridge.league_to_skill_group ltsg ON m."skillGroupId" = ltsg."skillGroupId"
    INNER JOIN mledb.series s ON (s.fixture_id = f.id
        AND UPPER(s."mode") = UPPER(gm.description)
        AND s.league = ltsg.league)
      INNER JOIN sprocket.schedule_group sg ON sf."scheduleGroupId" = sg.id
    WHERE
      sg."parentGroupId" = 291
      -- Season 18 is SG 291
)
  INSERT INTO mledb_bridge.series_to_match_parent ("seriesId", "matchParentId")
  SELECT
    mledb_series,
    sprocket_match_parent
  FROM
    m2m;
