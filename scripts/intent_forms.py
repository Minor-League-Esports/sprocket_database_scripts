from sqlalchemy import create_engine, text
import os
import csv

credstr = os.environ.get('POSTGRES_CREDS') # format is username:password
engine = create_engine(f'postgresql+psycopg2://{credstr}@spr.ocket.cloud:30000/sprocket_main')

basicUpdateQuery = """
UPDATE mledb.player AS mp
SET team_name=c.new_team
FROM (values
{}) as c(mleid, new_team)
WHERE mp.mleid=c.mleid
"""

selectQuery = """
    SELECT * FROM mledb.player AS mp
    WHERE mp.mleid='{}'
"""

fullPlayerTable = """
    SELECT * FROM mledb.player AS mp
"""

dryRun = False
players = {}

with engine.connect() as conn:
    # First, read the current playerbase from the DB
    fullTable = conn.execute(text(fullPlayerTable))
    for row in fullTable:
        did, name, mleid = row[14], row[6], row[5]
        # Default to FP, since if they didn't respond that's where they're headed
        players[did] = (mleid, name, 'FP')
        
    # Read the responses from the input CSV file
    with open('inputs/mlebb_retentions.csv') as csvfile:
        reader = csv.reader(csvfile)
        for i,row in enumerate(reader):
            if i == 0:
                continue

            # This is the format of the CSV from MLEBB
            # discord id,name,mleid,retention,team,league
            did, name, _, resp, team, _ = row

            # Responses are one of (Retain, FA, Former Player)
            if resp == 'Retention Eligible':
                new_team = team
            elif resp == 'Release to FA':
                new_team = 'FA'
            else:
                new_team = 'FP'
            
            # Update the players dictionary with the new response
            mleid, name, _ = players[did]
            players[did] = (mleid, name, new_team)
            
    values = ''
    for did, t in players.items():
        mleid, name, new_team = t
        if name == 'Nim' or name == 'Spike':
            print(f'{mleid}, {did}, {name}, {new_team}')
        values += f"({mleid}, '{new_team}'),\n"

    values = values[:-2]
    # Now let's put it into the DB:
    queryStr = basicUpdateQuery.format(values)
    if not dryRun:
        conn.execute(text(queryStr))
        conn.commit()
