from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import csv
import os

# Parse CSV
filepath = "ncps.csv"

parsed_data = []
with open(filepath) as csvfile:
    reader = csv.reader(csvfile)

    # Skip the header row
    header = next(reader)

    for row in reader:
        # First 5 columns are fixed
        match_id = row[0]
        team = row[1]
        league = row[2]
        mode = row[3]

        # Everything from index 4 onwards are the 'slots'
        # We filter out empty strings to handle the trailing commas
        slots = [slot for slot in row[4:] if slot.strip()]

        parsed_data.append(
            {
                "match_id": match_id,
                "team": team,
                "league": league,
                "mode": mode,
                "slots": slots,
            }
        )

# Connect to DB
username = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "postgres")
hostname = os.environ.get("DB_HOST", "localhost")
port = os.environ.get("DB_PORT", "25060")
database = os.environ.get("DB_NAME", "sprocket")

connstr = f"postgresql+psycopg2://{username}:{password}@{hostname}:{port}/{database}"
engine = create_engine(connstr)

# Translate match ID to series ID
query = """
    SELECT s.id, m.id
    FROM mledb.series s
    INNER JOIN mledb_bridge.series_to_match_parent s2mp on s2mp."seriesId" = s.id
    INNER JOIN sprocket.match_parent mp on mp.id = s2mp."matchParentId"
    INNER JOIN sprocket.match m on m."matchParentId" = mp.id
"""

match_to_series = {}
with engine.connect() as conn:
    result = conn.execute(text(query))
    for row in result:
        match_to_series[row[1]] = row[0]

    code_to_league = {
        "FL": "FOUNDATION",
        "AL": "ACADEMY",
        "CL": "CHAMPION",
        "ML": "MASTER",
        "PL": "PREMIER",
    }

    # Build Insert Statement
    query = """
    INSERT INTO mledb.team_role_usage (created_by, updated_by, team_name, league, series_id, role)
    VALUES
    """
    # ('Nigel', 'Nigel', 'Sabres', 'FOUNDATION', 68399, 'PLAYERB')
    for row in parsed_data:
        series_id = match_to_series[int(row["match_id"])]
        league = code_to_league[row["league"]]
        row_str = f"('Nigel', 'Nigel', '{row['team']}', '{league}', '{series_id}', "
        for slot in row["slots"]:
            slot_str = f"{row_str} 'PLAYER{slot.strip()}'),\n"
            query += slot_str
            query += slot_str
            query += slot_str

    # Make sure the insert statement is valid SQL, trailing commas aren't allowed.
    query = query[:-2]
    query += "\nON CONFLICT DO NOTHING;"

    # SHIP IT
    result = conn.execute(text(query))
    conn.commit()
    print(result)
