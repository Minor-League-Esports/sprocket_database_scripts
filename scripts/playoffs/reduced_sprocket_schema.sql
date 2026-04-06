--
-- Name: mledb_bridge; Type: SCHEMA; Schema: -; Owner: sprocket_main
--
CREATE SCHEMA mledb_bridge;

ALTER SCHEMA mledb_bridge OWNER TO sprocket_main;

SET
    default_tablespace = '';

SET
    default_table_access_method = heap;

--
-- Name: player_to_player; Type: TABLE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE TABLE mledb_bridge.player_to_player (
    id integer NOT NULL,
    "mledPlayerId" integer NOT NULL,
    "sprocketPlayerId" integer NOT NULL
);

ALTER TABLE mledb_bridge.player_to_player OWNER TO sprocket_main;

--
-- Name: division_to_franchise_group; Type: TABLE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE TABLE mledb_bridge.division_to_franchise_group (
    id integer NOT NULL,
    divison character varying NOT NULL,
    "franchiseGroupId" integer NOT NULL
);

ALTER TABLE mledb_bridge.division_to_franchise_group OWNER TO sprocket_main;

--
-- Name: division_to_franchise_group_id_seq; Type: SEQUENCE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE SEQUENCE mledb_bridge.division_to_franchise_group_id_seq AS integer START
WITH
    1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER TABLE mledb_bridge.division_to_franchise_group_id_seq OWNER TO sprocket_main;

--
-- Name: division_to_franchise_group_id_seq; Type: SEQUENCE OWNED BY; Schema: mledb_bridge; Owner: sprocket_main
--
ALTER SEQUENCE mledb_bridge.division_to_franchise_group_id_seq OWNED BY mledb_bridge.division_to_franchise_group.id;

--
-- Name: fixture_to_fixture; Type: TABLE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE TABLE mledb_bridge.fixture_to_fixture (
    id integer NOT NULL,
    "mleFixtureId" integer NOT NULL,
    "sprocketFixtureId" integer NOT NULL
);

ALTER TABLE mledb_bridge.fixture_to_fixture OWNER TO sprocket_main;

--
-- Name: fixture_to_fixture_id_seq; Type: SEQUENCE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE SEQUENCE mledb_bridge.fixture_to_fixture_id_seq AS integer START
WITH
    1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER TABLE mledb_bridge.fixture_to_fixture_id_seq OWNER TO sprocket_main;

--
-- Name: fixture_to_fixture_id_seq; Type: SEQUENCE OWNED BY; Schema: mledb_bridge; Owner: sprocket_main
--
ALTER SEQUENCE mledb_bridge.fixture_to_fixture_id_seq OWNED BY mledb_bridge.fixture_to_fixture.id;

--
-- Name: league_to_skill_group; Type: TABLE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE TABLE mledb_bridge.league_to_skill_group (
    id integer NOT NULL,
    league character varying NOT NULL,
    "skillGroupId" integer NOT NULL
);

ALTER TABLE mledb_bridge.league_to_skill_group OWNER TO sprocket_main;

--
-- Name: league_to_skill_group_id_seq; Type: SEQUENCE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE SEQUENCE mledb_bridge.league_to_skill_group_id_seq AS integer START
WITH
    1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER TABLE mledb_bridge.league_to_skill_group_id_seq OWNER TO sprocket_main;

--
-- Name: league_to_skill_group_id_seq; Type: SEQUENCE OWNED BY; Schema: mledb_bridge; Owner: sprocket_main
--
ALTER SEQUENCE mledb_bridge.league_to_skill_group_id_seq OWNED BY mledb_bridge.league_to_skill_group.id;

--
-- Name: match_to_schedule_group; Type: TABLE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE TABLE mledb_bridge.match_to_schedule_group (
    id integer NOT NULL,
    "matchId" integer NOT NULL,
    "weekScheduleGroupId" integer NOT NULL
);

ALTER TABLE mledb_bridge.match_to_schedule_group OWNER TO sprocket_main;

--
-- Name: match_to_schedule_group_id_seq; Type: SEQUENCE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE SEQUENCE mledb_bridge.match_to_schedule_group_id_seq AS integer START
WITH
    1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER TABLE mledb_bridge.match_to_schedule_group_id_seq OWNER TO sprocket_main;

--
-- Name: match_to_schedule_group_id_seq; Type: SEQUENCE OWNED BY; Schema: mledb_bridge; Owner: sprocket_main
--
ALTER SEQUENCE mledb_bridge.match_to_schedule_group_id_seq OWNED BY mledb_bridge.match_to_schedule_group.id;

--
-- Name: player_to_player_id_seq; Type: SEQUENCE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE SEQUENCE mledb_bridge.player_to_player_id_seq AS integer START
WITH
    1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER TABLE mledb_bridge.player_to_player_id_seq OWNER TO sprocket_main;

--
-- Name: player_to_player_id_seq; Type: SEQUENCE OWNED BY; Schema: mledb_bridge; Owner: sprocket_main
--
ALTER SEQUENCE mledb_bridge.player_to_player_id_seq OWNED BY mledb_bridge.player_to_player.id;

--
-- Name: player_to_user; Type: TABLE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE TABLE mledb_bridge.player_to_user (
    id integer NOT NULL,
    "playerId" integer NOT NULL,
    "userId" integer NOT NULL
);

ALTER TABLE mledb_bridge.player_to_user OWNER TO sprocket_main;

--
-- Name: player_to_user_id_seq; Type: SEQUENCE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE SEQUENCE mledb_bridge.player_to_user_id_seq AS integer START
WITH
    1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER TABLE mledb_bridge.player_to_user_id_seq OWNER TO sprocket_main;

--
-- Name: player_to_user_id_seq; Type: SEQUENCE OWNED BY; Schema: mledb_bridge; Owner: sprocket_main
--
ALTER SEQUENCE mledb_bridge.player_to_user_id_seq OWNED BY mledb_bridge.player_to_user.id;

--
-- Name: season_to_schedule_group; Type: TABLE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE TABLE mledb_bridge.season_to_schedule_group (
    id integer NOT NULL,
    "seasonNumber" integer NOT NULL,
    "scheduleGroupId" integer NOT NULL
);

ALTER TABLE mledb_bridge.season_to_schedule_group OWNER TO sprocket_main;

--
-- Name: season_to_schedule_group_id_seq; Type: SEQUENCE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE SEQUENCE mledb_bridge.season_to_schedule_group_id_seq AS integer START
WITH
    1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER TABLE mledb_bridge.season_to_schedule_group_id_seq OWNER TO sprocket_main;

--
-- Name: season_to_schedule_group_id_seq; Type: SEQUENCE OWNED BY; Schema: mledb_bridge; Owner: sprocket_main
--
ALTER SEQUENCE mledb_bridge.season_to_schedule_group_id_seq OWNED BY mledb_bridge.season_to_schedule_group.id;

--
-- Name: series_to_match_parent; Type: TABLE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE TABLE mledb_bridge.series_to_match_parent (
    id integer NOT NULL,
    "seriesId" integer NOT NULL,
    "matchParentId" integer NOT NULL
);

ALTER TABLE mledb_bridge.series_to_match_parent OWNER TO sprocket_main;

--
-- Name: series_to_match_parent_id_seq; Type: SEQUENCE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE SEQUENCE mledb_bridge.series_to_match_parent_id_seq AS integer START
WITH
    1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER TABLE mledb_bridge.series_to_match_parent_id_seq OWNER TO sprocket_main;

--
-- Name: series_to_match_parent_id_seq; Type: SEQUENCE OWNED BY; Schema: mledb_bridge; Owner: sprocket_main
--
ALTER SEQUENCE mledb_bridge.series_to_match_parent_id_seq OWNED BY mledb_bridge.series_to_match_parent.id;

--
-- Name: team_to_franchise; Type: TABLE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE TABLE mledb_bridge.team_to_franchise (
    id integer NOT NULL,
    team character varying NOT NULL,
    "franchiseId" integer NOT NULL
);

ALTER TABLE mledb_bridge.team_to_franchise OWNER TO sprocket_main;

--
-- Name: team_to_franchise_id_seq; Type: SEQUENCE; Schema: mledb_bridge; Owner: sprocket_main
--
CREATE SEQUENCE mledb_bridge.team_to_franchise_id_seq AS integer START
WITH
    1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
