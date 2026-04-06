import sys
import csv
import os
import argparse
import uuid
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database.objects import sScheduleFixture, sMatchParent, sMatch, mFixture, mSeries, mbFixtures, mMatch

# Load environment variables
load_dotenv()

# Database connection parameters from environment variables
db_host = os.environ.get('POSTGRES_HOST')
db_port = os.environ.get('POSTGRES_PORT')
db_user = os.environ.get('POSTGRES_USERNAME')
db_password = os.environ.get('POSTGRES_PASSWORD')
db_name = os.environ.get('POSTGRES_DATABASE')

# Check if all required variables are set
if not all([db_host, db_port, db_user, db_password, db_name]):
    print("Error: One or more required database environment variables are not set.")
    print("Ensure POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_DATABASE are set.")
    sys.exit(1)

# Construct the database URL
DATABASE_URL = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Set up command line argument parsing
parser = argparse.ArgumentParser(description='Create playoff matches from CSV data')
parser.add_argument('csv_file', help='Path to the CSV file containing match data')
parser.add_argument('--dry-run', action='store_true', help='Only print SQL statements without executing them')
args = parser.parse_args()

csv_file_path = args.csv_file

# Create SQLAlchemy engine with enhanced logging for dry-run
if args.dry_run:
    engine = create_engine(DATABASE_URL, echo=True, echo_pool=True)

    # Add event listener to capture all SQL statements in dry-run mode
    sql_statements = []

    @event.listens_for(engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if statement.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            sql_statements.append(f"-- SQL Statement:\n{statement}\n-- Parameters: {parameters}\n")

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
    'Premier':1,
    'Master':2,
    'Champion':3,
    'Academy':4,
    'Foundation':5,
}

code2League = {
    'FL':'Foundation',
    'AL':'Academy',
    'CL':'Champion',
    'ML':'Master',
    'PL':'Premier'
}

match2scheduleGroup = {
    21:303,
    22:304,
    23:305,
    24:306,
}

matchDetails = {
    21: (176, "2025-05-08 04:00:00.000", "2025-05-12 03:59:00.000"), # match_id, from_date, to_date
    22: (177, "2025-05-15 04:00:00.000", "2025-05-19 03:59:00.000"),
    23: (178, "2025-05-22 04:00:00.000", "2025-05-26 03:59:00.000"),
    24: (179, "2025-05-29 04:00:00.000", "2025-06-09 03:59:00.000"),
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
                print("Warning: No mledb.match objects found for the specified match IDs.")

            # Open and read the CSV file
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                # Check if file is empty
                try:
                    # Peek at first row to ensure file has content
                    has_content = bool(next(reader, None))
                    # Reset file pointer
                    csvfile.seek(0)
                    reader = csv.reader(csvfile)
                    if not has_content:
                        print(f"Error: CSV file {csv_file_path} is empty.")
                        # Skip to the end of the with block
                        reader = []  # Empty the reader to skip processing
                except Exception as e:
                    print(f"Error reading CSV file: {e}")
                    # Skip to the end of the with block
                    reader = []  # Empty the reader to skip processing
                for i, row in enumerate(reader):
                    if i == 0: # Skip header row
                        continue

                    # Skip empty rows or rows with insufficient columns
                    if len(row) < 5:
                        print(f"Skipping row {i+1}: Row has insufficient columns (expected 5, got {len(row)})")
                        continue

                    # Extract data from CSV row
                    gameModeStr = row[2]
                    # Map game mode string to ID
                    if gameModeStr == 'Standard':
                        gameModeId = 14
                    else:
                        gameModeId = 13 # Assuming other modes map to 13

                    leagueStr = code2League.get(row[1])
                    if not leagueStr:
                         print(f"Skipping row {i+1}: Unknown league code '{row[1]}'")
                         continue

                    skillGroupId = leaguestr2skillgroupid.get(leagueStr)
                    if skillGroupId is None:
                         print(f"Skipping row {i+1}: Unknown skill group for league '{leagueStr}'")
                         continue

                    try:
                        matchNumber = int(row[0])
                    except ValueError:
                        print(f"Skipping row {i+1}: Invalid match number '{row[0]}'")
                        continue

                    homeName = row[3]
                    awayName = row[4]

                    homeId = franchiseNameToId.get(homeName)
                    if homeId is None:
                         print(f"Skipping row {i+1}: Unknown home franchise '{homeName}'")
                         continue
                    awayId = franchiseNameToId.get(awayName)
                    if awayId is None:
                         print(f"Skipping row {i+1}: Unknown away franchise '{awayName}'")
                         continue

                    scheduleGroupId = match2scheduleGroup.get(matchNumber)
                    if scheduleGroupId is None:
                         print(f"Skipping row {i+1}: Unknown schedule group for match number '{matchNumber}'")
                         continue

                    match_detail = matchDetails.get(matchNumber)
                    if not match_detail:
                        print(f"Skipping row {i+1}: No match details found for match number '{matchNumber}'")
                        continue

                    mledb_match_id_for_fixture = match_detail[0]
                    mledb_match_instance = mledb_matches.get(mledb_match_id_for_fixture)

                    if not mledb_match_instance:
                        print(f"Skipping row {i+1}: Could not find mledb.match object for match number '{matchNumber}' (ID {mledb_match_id_for_fixture})")
                        continue

                    # --- Create and link ORM objects ---

                    # Sprocket Path
                    # Create sScheduleFixture
                    sprocket_fixture = sScheduleFixture(
                        scheduleGroupId=scheduleGroupId,
                        homeFranchiseId=homeId,
                        awayFranchiseId=awayId
                        # createdAt, updatedAt have defaults
                    )
                    session.add(sprocket_fixture)
                    # After adding, SQLAlchemy might not assign the ID immediately.
                    # Use session.flush() if you need the ID before commit,
                    # but relationships often don't require explicit ID handling.

                    # Create sMatchParent, linking to sScheduleFixture
                    match_parent = sMatchParent(
                        fixture=sprocket_fixture,
                        # createdAt, updatedAt have defaults
                    )
                    session.add(match_parent)

                    # Create sMatch, linking to sMatchParent
                    sprocket_match = sMatch(
                        match_parent=match_parent,
                        skillGroupId=skillGroupId,
                        gameModeId=gameModeId,
                        # isDummy has default=False
                        submissionId=f'match-{str(uuid.uuid4())}',
                        # submissionId is nullable, can be left as None or set explicitly
                        # createdAt, updatedAt have defaults
                    )
                    session.add(sprocket_match)

                    # MLEDB Path
                    # Check for existing mledb.fixture
                    mledb_fixture = session.query(mFixture).filter(
                        mFixture.match_id == mledb_match_instance.id,
                        mFixture.home_name == homeName,
                        mFixture.away_name == awayName
                    ).first()

                    if mledb_fixture is None:
                        # Create new mFixture if not found, linking to mledb.match
                        mledb_fixture = mFixture(
                            mledb_match=mledb_match_instance,
                            home_name=homeName,
                            away_name=awayName
                            # created_by, created_at, updated_by, updated_at have defaults
                            # channel_id has default=''
                        )
                        session.add(mledb_fixture)
                    else:
                        print(f"Warning: Found existing mledb.fixture for {homeName} vs {awayName} (Match ID: {mledb_match_instance.id}). Reusing existing fixture.")
                        # If reusing, ensure it's in the current session if not already
                        session.add(mledb_fixture)


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

                    # Bridge Path
                    # Create mbFixtures, linking Sprocket and MLEDB fixtures
                    bridge_entry = mbFixtures(
                        sprocket_fixture=sprocket_fixture,
                        mle_fixture=mledb_fixture
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
                print(f"Data from {csv_file_path} would be inserted with the above SQL.")
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
