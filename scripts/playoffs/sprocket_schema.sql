--
-- PostgreSQL database dump
--

-- Dumped from database version 13.6
-- Dumped by pg_dump version 14.17 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: mledb; Type: SCHEMA; Schema: -; Owner: sprocket_main
--

CREATE SCHEMA mledb;


ALTER SCHEMA mledb OWNER TO sprocket_main;

--
-- Name: sprocket; Type: SCHEMA; Schema: -; Owner: sprocket_main
--

CREATE SCHEMA sprocket;


ALTER SCHEMA sprocket OWNER TO sprocket_main;

CREATE TABLE mledb.fixture (
    id integer NOT NULL,
    created_by character varying(255) DEFAULT 'Unknown'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_by character varying(255) DEFAULT 'Unknown'::character varying NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    home_name character varying(255) NOT NULL,
    away_name character varying(255) NOT NULL,
    match_id integer NOT NULL,
    channel_id character varying(255) DEFAULT ''::character varying NOT NULL
);

CREATE TABLE mledb.match (
    id integer NOT NULL,
    created_by character varying(255) DEFAULT 'Unknown'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_by character varying(255) DEFAULT 'Unknown'::character varying NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    "from" timestamp(0) with time zone NOT NULL,
    "to" timestamp(0) with time zone NOT NULL,
    is_double_header boolean NOT NULL,
    season integer NOT NULL,
    match_number integer NOT NULL,
    map character varying(255) DEFAULT 'CHAMPIONS_FIELD'::character varying NOT NULL
);

CREATE TABLE mledb.season (
    season_number integer NOT NULL,
    created_by character varying(255) DEFAULT 'Unknown'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_by character varying(255) DEFAULT 'Unknown'::character varying NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    start_date timestamp(0) with time zone NOT NULL,
    end_date timestamp(0) with time zone NOT NULL,
    roster_locked boolean DEFAULT false NOT NULL,
    week_length integer DEFAULT 7 NOT NULL
);

CREATE TABLE mledb.series (
    id integer NOT NULL,
    created_by character varying(255) DEFAULT 'Unknown'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_by character varying(255) DEFAULT 'Unknown'::character varying NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    league character varying(255) DEFAULT 'UNKNOWN'::character varying NOT NULL,
    submission_timestamp timestamp(0) with time zone,
    scheduled_time timestamp(0) with time zone,
    full_ncp boolean DEFAULT false NOT NULL,
    mode text NOT NULL,
    fixture_id integer,
    scrim_id integer,
    stream_event_message_id character varying(255),
    CONSTRAINT series_mode_check CHECK ((mode = ANY (ARRAY['SOLO'::text, 'DOUBLES'::text, 'STANDARD'::text])))
);

CREATE TABLE sprocket.match (
    id integer NOT NULL,
    "createdAt" timestamp without time zone DEFAULT now() NOT NULL,
    "updatedAt" timestamp without time zone DEFAULT now() NOT NULL,
    "deletedAt" timestamp without time zone,
    "isDummy" boolean DEFAULT false NOT NULL,
    "submissionId" character varying,
    "skillGroupId" integer NOT NULL,
    "matchParentId" integer,
    "gameModeId" integer,
    "invalidationId" integer
);

CREATE TABLE sprocket.match_parent (
    id integer NOT NULL,
    "createdAt" timestamp without time zone DEFAULT now() NOT NULL,
    "updatedAt" timestamp without time zone DEFAULT now() NOT NULL,
    "deletedAt" timestamp without time zone,
    "eventId" integer,
    "scrimMetaId" integer,
    "fixtureId" integer
);

CREATE TABLE sprocket.schedule_fixture (
    id integer NOT NULL,
    "createdAt" timestamp without time zone DEFAULT now() NOT NULL,
    "updatedAt" timestamp without time zone DEFAULT now() NOT NULL,
    "deletedAt" timestamp without time zone,
    "scheduleGroupId" integer,
    "homeFranchiseId" integer,
    "awayFranchiseId" integer
);

CREATE TABLE sprocket.schedule_group (
    id integer NOT NULL,
    "createdAt" timestamp without time zone DEFAULT now() NOT NULL,
    "updatedAt" timestamp without time zone DEFAULT now() NOT NULL,
    "deletedAt" timestamp without time zone,
    start timestamp without time zone NOT NULL,
    "end" timestamp without time zone NOT NULL,
    description character varying,
    "typeId" integer,
    "gameId" integer,
    "parentGroupId" integer
);

CREATE TABLE sprocket.schedule_group_type (
    id integer NOT NULL,
    "createdAt" timestamp without time zone DEFAULT now() NOT NULL,
    "updatedAt" timestamp without time zone DEFAULT now() NOT NULL,
    "deletedAt" timestamp without time zone,
    name character varying NOT NULL,
    code character varying NOT NULL,
    "organizationId" integer
);
--
-- PostgreSQL database dump
--

-- Dumped from database version 13.6
-- Dumped by pg_dump version 14.17 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: mledb_bridge; Type: SCHEMA; Schema: -; Owner: sprocket_main
--

CREATE SCHEMA mledb_bridge;


ALTER SCHEMA mledb_bridge OWNER TO sprocket_main;

SET default_tablespace = '';

SET default_table_access_method = heap;

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

CREATE SEQUENCE mledb_bridge.division_to_franchise_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


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

CREATE SEQUENCE mledb_bridge.fixture_to_fixture_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


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

CREATE SEQUENCE mledb_bridge.league_to_skill_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


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

CREATE SEQUENCE mledb_bridge.match_to_schedule_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE mledb_bridge.match_to_schedule_group_id_seq OWNER TO sprocket_main;

--
-- Name: match_to_schedule_group_id_seq; Type: SEQUENCE OWNED BY; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER SEQUENCE mledb_bridge.match_to_schedule_group_id_seq OWNED BY mledb_bridge.match_to_schedule_group.id;


--
-- Name: player_to_player_id_seq; Type: SEQUENCE; Schema: mledb_bridge; Owner: sprocket_main
--

CREATE SEQUENCE mledb_bridge.player_to_player_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


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

CREATE SEQUENCE mledb_bridge.player_to_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


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

CREATE SEQUENCE mledb_bridge.season_to_schedule_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


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

CREATE SEQUENCE mledb_bridge.series_to_match_parent_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


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

CREATE SEQUENCE mledb_bridge.team_to_franchise_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE mledb_bridge.team_to_franchise_id_seq OWNER TO sprocket_main;

--
-- Name: team_to_franchise_id_seq; Type: SEQUENCE OWNED BY; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER SEQUENCE mledb_bridge.team_to_franchise_id_seq OWNED BY mledb_bridge.team_to_franchise.id;


--
-- Name: division_to_franchise_group id; Type: DEFAULT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.division_to_franchise_group ALTER COLUMN id SET DEFAULT nextval('mledb_bridge.division_to_franchise_group_id_seq'::regclass);


--
-- Name: fixture_to_fixture id; Type: DEFAULT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.fixture_to_fixture ALTER COLUMN id SET DEFAULT nextval('mledb_bridge.fixture_to_fixture_id_seq'::regclass);


--
-- Name: league_to_skill_group id; Type: DEFAULT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.league_to_skill_group ALTER COLUMN id SET DEFAULT nextval('mledb_bridge.league_to_skill_group_id_seq'::regclass);


--
-- Name: match_to_schedule_group id; Type: DEFAULT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.match_to_schedule_group ALTER COLUMN id SET DEFAULT nextval('mledb_bridge.match_to_schedule_group_id_seq'::regclass);


--
-- Name: player_to_player id; Type: DEFAULT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.player_to_player ALTER COLUMN id SET DEFAULT nextval('mledb_bridge.player_to_player_id_seq'::regclass);


--
-- Name: player_to_user id; Type: DEFAULT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.player_to_user ALTER COLUMN id SET DEFAULT nextval('mledb_bridge.player_to_user_id_seq'::regclass);


--
-- Name: season_to_schedule_group id; Type: DEFAULT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.season_to_schedule_group ALTER COLUMN id SET DEFAULT nextval('mledb_bridge.season_to_schedule_group_id_seq'::regclass);


--
-- Name: series_to_match_parent id; Type: DEFAULT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.series_to_match_parent ALTER COLUMN id SET DEFAULT nextval('mledb_bridge.series_to_match_parent_id_seq'::regclass);


--
-- Name: team_to_franchise id; Type: DEFAULT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.team_to_franchise ALTER COLUMN id SET DEFAULT nextval('mledb_bridge.team_to_franchise_id_seq'::regclass);


--
-- Name: player_to_user PK_006742d1c2d56a8fd4dd56f765b; Type: CONSTRAINT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.player_to_user
    ADD CONSTRAINT "PK_006742d1c2d56a8fd4dd56f765b" PRIMARY KEY (id);


--
-- Name: team_to_franchise PK_360038235154676aac26564281d; Type: CONSTRAINT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.team_to_franchise
    ADD CONSTRAINT "PK_360038235154676aac26564281d" PRIMARY KEY (id);


--
-- Name: series_to_match_parent PK_4754d726fb515e21b0197fc055b; Type: CONSTRAINT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.series_to_match_parent
    ADD CONSTRAINT "PK_4754d726fb515e21b0197fc055b" PRIMARY KEY (id);


--
-- Name: player_to_player PK_519f5d30db16a620f0f29b987b2; Type: CONSTRAINT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.player_to_player
    ADD CONSTRAINT "PK_519f5d30db16a620f0f29b987b2" PRIMARY KEY (id);


--
-- Name: league_to_skill_group PK_8512c6e65c876c277627a76b1d6; Type: CONSTRAINT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.league_to_skill_group
    ADD CONSTRAINT "PK_8512c6e65c876c277627a76b1d6" PRIMARY KEY (id);


--
-- Name: fixture_to_fixture PK_95d56618cb4b72434cb19380f76; Type: CONSTRAINT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.fixture_to_fixture
    ADD CONSTRAINT "PK_95d56618cb4b72434cb19380f76" PRIMARY KEY (id);


--
-- Name: match_to_schedule_group PK_b403106d0b8a6a7785299fc0baf; Type: CONSTRAINT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.match_to_schedule_group
    ADD CONSTRAINT "PK_b403106d0b8a6a7785299fc0baf" PRIMARY KEY (id);


--
-- Name: division_to_franchise_group PK_d8756b189a98d02d751f0ff1132; Type: CONSTRAINT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.division_to_franchise_group
    ADD CONSTRAINT "PK_d8756b189a98d02d751f0ff1132" PRIMARY KEY (id);


--
-- Name: season_to_schedule_group PK_e5df4f78a0f1cb2178d9aa6d2d0; Type: CONSTRAINT; Schema: mledb_bridge; Owner: sprocket_main
--

ALTER TABLE ONLY mledb_bridge.season_to_schedule_group
    ADD CONSTRAINT "PK_e5df4f78a0f1cb2178d9aa6d2d0" PRIMARY KEY (id);


--
-- Name: SCHEMA mledb_bridge; Type: ACL; Schema: -; Owner: sprocket_main
--

GRANT USAGE ON SCHEMA mledb_bridge TO sprocket_main_data_science;
GRANT USAGE ON SCHEMA mledb_bridge TO sprocket_main_legacy_ro;


--
-- Name: TABLE player_to_player; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT SELECT ON TABLE mledb_bridge.player_to_player TO sprocket_main_data_science;
GRANT SELECT ON TABLE mledb_bridge.player_to_player TO "data_science_main-github-bwpikaard-1663106768";
GRANT SELECT ON TABLE mledb_bridge.player_to_player TO sprocket_main_legacy_ro;


--
-- Name: TABLE division_to_franchise_group; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT SELECT ON TABLE mledb_bridge.division_to_franchise_group TO sprocket_main_data_science;
GRANT SELECT ON TABLE mledb_bridge.division_to_franchise_group TO sprocket_main_legacy_ro;


--
-- Name: SEQUENCE division_to_franchise_group_id_seq; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT ALL ON SEQUENCE mledb_bridge.division_to_franchise_group_id_seq TO sprocket_main_data_science;


--
-- Name: TABLE fixture_to_fixture; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT SELECT ON TABLE mledb_bridge.fixture_to_fixture TO sprocket_main_data_science;
GRANT SELECT ON TABLE mledb_bridge.fixture_to_fixture TO sprocket_main_legacy_ro;


--
-- Name: SEQUENCE fixture_to_fixture_id_seq; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT ALL ON SEQUENCE mledb_bridge.fixture_to_fixture_id_seq TO sprocket_main_data_science;


--
-- Name: TABLE league_to_skill_group; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT SELECT ON TABLE mledb_bridge.league_to_skill_group TO sprocket_main_data_science;
GRANT SELECT ON TABLE mledb_bridge.league_to_skill_group TO sprocket_main_legacy_ro;


--
-- Name: SEQUENCE league_to_skill_group_id_seq; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT ALL ON SEQUENCE mledb_bridge.league_to_skill_group_id_seq TO sprocket_main_data_science;


--
-- Name: TABLE match_to_schedule_group; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT SELECT ON TABLE mledb_bridge.match_to_schedule_group TO sprocket_main_data_science;
GRANT SELECT ON TABLE mledb_bridge.match_to_schedule_group TO sprocket_main_legacy_ro;


--
-- Name: SEQUENCE match_to_schedule_group_id_seq; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT ALL ON SEQUENCE mledb_bridge.match_to_schedule_group_id_seq TO sprocket_main_data_science;


--
-- Name: SEQUENCE player_to_player_id_seq; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT ALL ON SEQUENCE mledb_bridge.player_to_player_id_seq TO sprocket_main_data_science;


--
-- Name: TABLE player_to_user; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT SELECT ON TABLE mledb_bridge.player_to_user TO sprocket_main_data_science;
GRANT SELECT ON TABLE mledb_bridge.player_to_user TO sprocket_main_legacy_ro;


--
-- Name: SEQUENCE player_to_user_id_seq; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT ALL ON SEQUENCE mledb_bridge.player_to_user_id_seq TO sprocket_main_data_science;


--
-- Name: TABLE season_to_schedule_group; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT SELECT ON TABLE mledb_bridge.season_to_schedule_group TO sprocket_main_data_science;
GRANT SELECT ON TABLE mledb_bridge.season_to_schedule_group TO sprocket_main_legacy_ro;


--
-- Name: SEQUENCE season_to_schedule_group_id_seq; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT ALL ON SEQUENCE mledb_bridge.season_to_schedule_group_id_seq TO sprocket_main_data_science;


--
-- Name: TABLE series_to_match_parent; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT SELECT ON TABLE mledb_bridge.series_to_match_parent TO sprocket_main_data_science;
GRANT SELECT ON TABLE mledb_bridge.series_to_match_parent TO sprocket_main_legacy_ro;


--
-- Name: SEQUENCE series_to_match_parent_id_seq; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT ALL ON SEQUENCE mledb_bridge.series_to_match_parent_id_seq TO sprocket_main_data_science;


--
-- Name: TABLE team_to_franchise; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT SELECT ON TABLE mledb_bridge.team_to_franchise TO sprocket_main_data_science;
GRANT SELECT ON TABLE mledb_bridge.team_to_franchise TO sprocket_main_legacy_ro;


--
-- Name: SEQUENCE team_to_franchise_id_seq; Type: ACL; Schema: mledb_bridge; Owner: sprocket_main
--

GRANT ALL ON SEQUENCE mledb_bridge.team_to_franchise_id_seq TO sprocket_main_data_science;


--
-- PostgreSQL database dump complete
--

