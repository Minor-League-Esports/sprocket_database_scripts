import sys
import csv
import os
import argparse
import uuid
from sqlalchemy import create_engine, text, event, and_, or_
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database.objects import (
    sScheduleFixture,
    sMatchParent,
    sMatch,
    mFixture,
    mSeries,
    mbFixtures,
    mbSeriesToMatchParent,
    mMatch,
)

# Load environment variables
load_dotenv()

# Database connection parameters from environment variables
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_user = os.environ.get("DB_USERNAME")
db_password = os.environ.get("DB_PASSWORD")
db_name = os.environ.get("DB_DATABASE")

# Check if all required variables are set
if not all([db_host, db_port, db_user, db_password, db_name]):
    print("Error: One or more required database environment variables are not set.")
    print(
        "Ensure POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_DATABASE are set."
    )
    sys.exit(1)

# Construct the database URL
DATABASE_URL = (
    f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

# Set up command line argument parsing
parser = argparse.ArgumentParser(description="Create playoff matches from CSV data")
parser.add_argument("csv_file", help="Path to the CSV file containing match data")
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Only print SQL statements without executing them",
)
args = parser.parse_args()

csv_file_path = args.csv_file

# Create SQLAlchemy engine with enhanced logging for dry-run
if args.dry_run:
    engine = create_engine(DATABASE_URL, echo=True, echo_pool=True)

    # Add event listener to capture all SQL statements in dry-run mode
    sql_statements = []

    @event.listens_for(engine, "before_cursor_execute")
    def receive_before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        if statement.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
            sql_statements.append(
                f"-- SQL Statement:\n{statement}\n-- Parameters: {parameters}\n"
            )

else:
    engine = create_engine(DATABASE_URL, echo=False)
    sql_statements = []

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQL query to get franchise names and IDs
queryStr = """
SELECT fp.title, fp."franchiseId" from sprocket.franchise_profile as fp;
"""

# Mapping dictionaries
leaguestr2skillgroupid = {
    "Premier": 1,
    "Master": 2,
    "Champion": 3,
    "Academy": 4,
    "Foundation": 5,
}

code2League = {
    "FL": "Foundation",
    "AL": "Academy",
    "CL": "Champion",
    "ML": "Master",
    "PL": "Premier",
}

match2scheduleGroup = {
    21: 352,
    22: 353,
    23: 354,
    24: 355,
}

matchDetails = {
    21: (
        220,
        "2026-04-27 04:00:00.000",
        "2026-05-04 03:59:00.000",
    ),  # match_id, from_date, to_date
    22: (221, "2026-05-04 04:00:00.000", "2026-05-11 03:59:00.000"),
    23: (222, "2026-05-11 04:00:00.000", "2026-05-25 03:59:00.000"),
    24: (223, "2026-05-25 04:00:00.000", "2026-06-01 03:59:00.000"),
}

# Use the session to interact with the database
with SessionLocal() as session:
    try:
        # Begin a transaction
        transaction = session.begin()

        try:
            # First, build a map from franchise name (home name, away name in the input)
            # to franchise ID using direct query (can be replaced by ORM query if needed)
            franchiseNameToId = {}
            # Use session.execute for raw SQL
            res = session.execute(text(queryStr))
            for row in res:
                title = row[0]
                franchiseId = row[1]
                franchiseNameToId[title] = franchiseId

            # Fetch mledb.match objects needed for fixtures before the loop
            mledb_matches = {}
            mledb_match_ids = [details[0] for details in matchDetails.values()]
            # Use ORM query to fetch objects
            stmt = session.query(mMatch).filter(mMatch.id.in_(mledb_match_ids))
            result = stmt.all()
            if result:  # Check if result is not None and not empty
                for mledb_match_obj in result:
                    mledb_matches[mledb_match_obj.id] = mledb_match_obj
            else:
                print(
                    "Warning: No mledb.match objects found for the specified match IDs."
                )

            sprocket_fixtures = {}
            mledb_fixtures = {}

            # Open and read the CSV file
            with open(csv_file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                # Check if file is empty
                try:
                    # Peek at first row to ensure file has content
                    has_content = bool(next(reader, None))
                    # Reset file pointer
                    csvfile.seek(0)
                    reader = csv.reader(csvfile)
                    if not has_content:
                        raise ValueError(f"CSV file {csv_file_path} is empty.")
                except Exception as e:
                    raise ValueError(f"Error reading CSV file: {e}") from e
                for i, row in enumerate(reader):
                    if i == 0:  # Skip header row
                        continue

                    # Skip empty rows or rows with insufficient columns
                    if len(row) < 5:
                        raise ValueError(
                            f"Row {i + 1} has insufficient columns (expected 5, got {len(row)})"
                        )

                    # Extract data from CSV row
                    gameModeStr = row[2]
                    # Map game mode string to ID
                    if gameModeStr.upper() == "STANDARD":
                        gameModeId = 14
                    else:
                        gameModeId = 13  # Assuming other modes map to 13

                    leagueStr = code2League.get(row[1])
                    if not leagueStr:
                        raise ValueError(
                            f"Row {i + 1} has unknown league code '{row[1]}'"
                        )

                    skillGroupId = leaguestr2skillgroupid.get(leagueStr)
                    if skillGroupId is None:
                        raise ValueError(
                            f"Row {i + 1} has unknown skill group for league '{leagueStr}'"
                        )

                    try:
                        matchNumber = int(row[0])
                    except ValueError:
                        raise ValueError(
                            f"Row {i + 1} has invalid match number '{row[0]}'"
                        )

                    homeName = row[3]
                    awayName = row[4]

                    homeId = franchiseNameToId.get(homeName)
                    if homeId is None:
                        raise ValueError(
                            f"Row {i + 1} has unknown home franchise '{homeName}'"
                        )
                    awayId = franchiseNameToId.get(awayName)
                    if awayId is None:
                        raise ValueError(
                            f"Row {i + 1} has unknown away franchise '{awayName}'"
                        )

                    scheduleGroupId = match2scheduleGroup.get(matchNumber)
                    if scheduleGroupId is None:
                        raise ValueError(
                            f"Row {i + 1} has unknown schedule group for match number '{matchNumber}'"
                        )

                    match_detail = matchDetails.get(matchNumber)
                    if not match_detail:
                        raise ValueError(
                            f"Row {i + 1} has no match details for match number '{matchNumber}'"
                        )

                    mledb_match_id_for_fixture = match_detail[0]
                    mledb_match_instance = mledb_matches.get(mledb_match_id_for_fixture)

                    if not mledb_match_instance:
                        raise ValueError(
                            f"Row {i + 1} could not find mledb.match object for match number '{matchNumber}' (ID {mledb_match_id_for_fixture})"
                        )

                    # --- Create and link ORM objects ---

                    # Reuse the same Sprocket schedule fixture for duplicate matchups
                    # in the same playoff week, regardless of which franchise is home/away.
                    # Separate match rows still get created below.
                    sprocket_fixture_key = (
                        scheduleGroupId,
                        frozenset((homeId, awayId)),
                    )
                    sprocket_fixture = sprocket_fixtures.get(sprocket_fixture_key)

                    if sprocket_fixture is None:
                        sprocket_fixture = (
                            session.query(sScheduleFixture)
                            .filter(
                                sScheduleFixture.scheduleGroupId == scheduleGroupId,
                                or_(
                                    and_(
                                        sScheduleFixture.homeFranchiseId == homeId,
                                        sScheduleFixture.awayFranchiseId == awayId,
                                    ),
                                    and_(
                                        sScheduleFixture.homeFranchiseId == awayId,
                                        sScheduleFixture.awayFranchiseId == homeId,
                                    ),
                                ),
                                sScheduleFixture.deletedAt.is_(None),
                            )
                            .first()
                        )

                    if sprocket_fixture is None:
                        sprocket_fixture = sScheduleFixture(
                            scheduleGroupId=scheduleGroupId,
                            homeFranchiseId=homeId,
                            awayFranchiseId=awayId,
                            # createdAt, updatedAt have defaults
                        )
                        session.add(sprocket_fixture)
                        session.flush()
                    else:
                        print(
                            f"Warning: Found existing sprocket.schedule_fixture for {homeName} vs {awayName} (Schedule Group ID: {scheduleGroupId}). Reusing existing fixture."
                        )
                        session.add(sprocket_fixture)

                    sprocket_fixtures[sprocket_fixture_key] = sprocket_fixture

                    # Create sMatchParent, linking to sScheduleFixture
                    match_parent = sMatchParent(
                        fixtureId=sprocket_fixture.id,
                        # createdAt, updatedAt have defaults
                    )
                    session.add(match_parent)

                    # Create sMatch, linking to sMatchParent
                    sprocket_match = sMatch(
                        match_parent=match_parent,
                        skillGroupId=skillGroupId,
                        gameModeId=gameModeId,
                        # isDummy has default=False
                        submissionId=f"match-{str(uuid.uuid4())}",
                        # submissionId is nullable, can be left as None or set explicitly
                        # createdAt, updatedAt have defaults
                    )
                    session.add(sprocket_match)

                    # MLEDB Path
                    # Reuse the same mledb.fixture for duplicate matchups in the same mledb.match.
                    mledb_fixture_key = (mledb_match_instance.id, homeName, awayName)
                    mledb_fixture = mledb_fixtures.get(mledb_fixture_key)

                    if mledb_fixture is None:
                        mledb_fixture = (
                            session.query(mFixture)
                            .filter(
                                mFixture.match_id == mledb_match_instance.id,
                                mFixture.home_name == homeName,
                                mFixture.away_name == awayName,
                            )
                            .first()
                        )

                    if mledb_fixture is None:
                        # Create new mFixture if not found, linking to mledb.match
                        mledb_fixture = mFixture(
                            mledb_match=mledb_match_instance,
                            home_name=homeName,
                            away_name=awayName,
                            # created_by, created_at, updated_by, updated_at have defaults
                            # channel_id has default=''
                        )
                        session.add(mledb_fixture)
                        session.flush()
                    else:
                        print(
                            f"Warning: Found existing mledb.fixture for {homeName} vs {awayName} (Match ID: {mledb_match_instance.id}). Reusing existing fixture."
                        )
                        # If reusing, ensure it's in the current session if not already
                        session.add(mledb_fixture)

                    mledb_fixtures[mledb_fixture_key] = mledb_fixture

                    # Create mSeries, linking to mledb.fixture
                    mledb_series = mSeries(
                        league=leagueStr.upper(),
                        mode=gameModeStr.upper(),
                        fixture=mledb_fixture,
                        # full_ncp has default=False
                        # updated_by has default='Playoffs'
                        # created_by, created_at, updated_by, updated_at have defaults
                        # submission_timestamp, scheduled_time, scrim_id, stream_event_message_id are nullable
                    )
                    session.add(mledb_series)

                    # Bridge each series to its Sprocket match parent (1:1 per CSV row)
                    series_bridge = mbSeriesToMatchParent(
                        series=mledb_series,
                        match_parent=match_parent,
                    )
                    session.add(series_bridge)

                    # Bridge Path
                    # Create mbFixtures only when this Sprocket/MLEDB fixture pair has not
                    # already been linked. Duplicate game-mode rows share the fixtures.
                    bridge_entry = (
                        session.query(mbFixtures)
                        .filter(
                            mbFixtures.sprocketFixtureId == sprocket_fixture.id,
                            mbFixtures.mleFixtureId == mledb_fixture.id,
                        )
                        .first()
                    )
                    if bridge_entry is None:
                        bridge_entry = mbFixtures(
                            sprocket_fixture=sprocket_fixture,
                            mle_fixture=mledb_fixture,
                            # id is primary key, will be generated
                        )
                        session.add(bridge_entry)

            # In dry-run mode, flush to generate SQL without committing
            if args.dry_run:
                print("\n=== Flushing session to generate INSERT statements ===")
                session.flush()
                print("\n=== Generated SQL Statements ===")
                if sql_statements:
                    for stmt in sql_statements:
                        print(stmt)
                else:
                    print("No INSERT/UPDATE/DELETE statements were generated.")
                print("\n=== Dry run completed ===")
                print(
                    f"Data from {csv_file_path} would be inserted with the above SQL."
                )
                # Explicitly roll back in dry run mode
                transaction.rollback()
            else:
                print(f"Successfully processed data from {csv_file_path}.")
                transaction.commit()

        except Exception as e:
            transaction.rollback()
            raise e

    except Exception as e:
        # If any exception occurs, the transaction will be rolled back above
        print(f"An error occurred: {e}")
        sys.exit(1)
