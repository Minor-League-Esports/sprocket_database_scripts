import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from database.objects import (
    mMatch,
    mSeason,
    mbMatchToScheduleGroup,
    mbSeasonToScheduleGroup,
    sScheduleGroup,
)


load_dotenv()


@dataclass(frozen=True)
class PlayoffWeek:
    match_number: int
    description: str
    start: datetime
    end: datetime


DEFAULT_PLAYOFF_WEEKS = [
    PlayoffWeek(
        match_number=21,
        description="Conference Quarterfinals",
        start=datetime.fromisoformat("2025-05-08 04:00:00"),
        end=datetime.fromisoformat("2025-05-12 03:59:00"),
    ),
    PlayoffWeek(
        match_number=22,
        description="Conference Semifinals",
        start=datetime.fromisoformat("2025-05-15 04:00:00"),
        end=datetime.fromisoformat("2025-05-19 03:59:00"),
    ),
    PlayoffWeek(
        match_number=23,
        description="Conference Finals",
        start=datetime.fromisoformat("2025-05-22 04:00:00"),
        end=datetime.fromisoformat("2025-05-26 03:59:00"),
    ),
    PlayoffWeek(
        match_number=24,
        description="Grand Finals",
        start=datetime.fromisoformat("2025-05-29 04:00:00"),
        end=datetime.fromisoformat("2025-06-09 03:59:00"),
    ),
]


def get_env_var(*names):
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def build_database_url():
    db_host = get_env_var("DB_HOST")
    db_port = get_env_var("DB_PORT")
    db_user = get_env_var("DB_USERNAME", "DB_USER")
    db_password = get_env_var("DB_PASSWORD")
    db_name = get_env_var("DB_DATABASE", "DB_NAME")

    if not all([db_host, db_port, db_user, db_password, db_name]):
        print("Error: One or more required database environment variables are not set.")
        print(
            "Ensure DB_HOST, DB_PORT, DB_USERNAME/DB_USER, DB_PASSWORD, and DB_DATABASE/DB_NAME are set."
        )
        sys.exit(1)

    return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def parse_datetime(value):
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"'{value}' is not a valid ISO datetime. Example: 2025-05-08 04:00:00"
        ) from exc


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create MLEDB and Sprocket playoff season/week containers."
    )
    parser.add_argument(
        "season_number",
        type=int,
        help="Season number to create for playoffs.",
    )
    parser.add_argument(
        "--season-description",
        default=None,
        help="Sprocket top-level schedule group description. Defaults to 'Season <season_number> Playoffs'.",
    )
    parser.add_argument(
        "--start",
        type=parse_datetime,
        default=None,
        help="Override season start timestamp. Defaults to the first playoff week start.",
    )
    parser.add_argument(
        "--end",
        type=parse_datetime,
        default=None,
        help="Override season end timestamp. Defaults to the last playoff week end.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Flush changes and print generated SQL, then roll back.",
    )
    return parser.parse_args()


def assert_not_exists(session, season_number):
    existing_season = session.get(mSeason, season_number)
    if existing_season is not None:
        raise ValueError(f"mledb.season {season_number} already exists")

    existing_matches = (
        session.query(mMatch)
        .filter(
            mMatch.season == season_number,
            mMatch.match_number.in_([week.match_number for week in DEFAULT_PLAYOFF_WEEKS]),
        )
        .all()
    )
    if existing_matches:
        match_numbers = ", ".join(
            str(match.match_number) for match in sorted(existing_matches, key=lambda item: item.match_number)
        )
        raise ValueError(
            f"mledb.match rows already exist for season {season_number}, match numbers: {match_numbers}"
        )


def create_playoff_schedule(session, season_number, season_description, season_start, season_end):
    assert_not_exists(session, season_number)

    mledb_season = mSeason(
        season_number=season_number,
        start_date=season_start,
        end_date=season_end,
    )
    session.add(mledb_season)

    sprocket_season_group = sScheduleGroup(
        start=season_start,
        end=season_end,
        description=season_description,
        typeId=1,
        gameId=7,
        parentGroupId=None,
    )
    session.add(sprocket_season_group)
    session.flush()

    season_bridge = mbSeasonToScheduleGroup(
        seasonNumber=season_number,
        scheduleGroupId=sprocket_season_group.id,
    )
    session.add(season_bridge)

    created_weeks = []
    for week in DEFAULT_PLAYOFF_WEEKS:
        print(f"Creating {week.description} (match {week.match_number})...")

        mledb_match = mMatch(
            from_date=week.start,
            to_date=week.end,
            is_double_header=False,
            season=season_number,
            match_number=week.match_number,
        )
        session.add(mledb_match)

        sprocket_week_group = sScheduleGroup(
            start=week.start,
            end=week.end,
            description=week.description,
            typeId=3,
            gameId=7,
            parentGroupId=sprocket_season_group.id,
        )
        session.add(sprocket_week_group)
        session.flush()

        bridge = mbMatchToScheduleGroup(
            matchId=mledb_match.id,
            weekScheduleGroupId=sprocket_week_group.id,
        )
        session.add(bridge)
        created_weeks.append((week, mledb_match.id, sprocket_week_group.id))

    return sprocket_season_group.id, created_weeks


def main():
    args = parse_args()
    season_start = args.start or DEFAULT_PLAYOFF_WEEKS[0].start
    season_end = args.end or DEFAULT_PLAYOFF_WEEKS[-1].end
    season_description = args.season_description or f"Season {args.season_number} Playoffs"

    engine = create_engine(build_database_url(), echo=args.dry_run, echo_pool=args.dry_run)
    sql_statements = []

    if args.dry_run:
        @event.listens_for(engine, "before_cursor_execute")
        def receive_before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            if statement.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                sql_statements.append(
                    f"-- SQL Statement:\n{statement}\n-- Parameters: {parameters}\n"
                )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with SessionLocal() as session:
        transaction = session.begin()
        try:
            sprocket_season_group_id, created_weeks = create_playoff_schedule(
                session,
                args.season_number,
                season_description,
                season_start,
                season_end,
            )

            if args.dry_run:
                print("\n=== Flushing session to generate INSERT statements ===")
                session.flush()
                print("\n=== Generated SQL Statements ===")
                if sql_statements:
                    for statement in sql_statements:
                        print(statement)
                else:
                    print("No INSERT/UPDATE/DELETE statements were generated.")
                print("\n=== Dry run completed; rolling back ===")
                transaction.rollback()
            else:
                transaction.commit()
                print(f"Created playoff season {args.season_number}.")
                print(f"Sprocket season schedule_group ID: {sprocket_season_group_id}")
                for week, match_id, schedule_group_id in created_weeks:
                    print(
                        f"- {week.description}: mledb.match ID {match_id}, sprocket.schedule_group ID {schedule_group_id}"
                    )
        except Exception as exc:
            transaction.rollback()
            print(f"An error occurred: {exc}")
            sys.exit(1)


if __name__ == "__main__":
    main()
