from datetime import datetime
import csv
import re

date_format = '%H:%M:%S %m/%d/%Y'
timestamp_format = '%Y-%m-%d %H:%M:%S -0700'
def convert_to_timestamp(time_str, date_str):
    return datetime.strptime(time_str + ' ' + date_str, date_format).strftime(timestamp_format)

# Get a dict from Franchise name to ID
franchises = {}
with open('input_data/franchises.csv') as csvfile:
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
        if i == 0:
            continue
        franchises[row[4]] = row[9]
        franchises[row[9]] = row[4]

# Read the original input file and parse it
gamemodes = ['Doubles', 'Standard']
leagues = ['Foundation', 'Academy', 'Champion', 'Master', 'Premier']

schedule_groups = {}
matches = []
with open('input_data/Schedule_Season_17_-_MatchData_1.csv') as csvfile:
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
        if i == 0:
            continue
        match_num, start_time, start_date, end_date = row[1], row[7], row[11], row[12]
        match_num = int(re.sub('Match ', '', match_num))
        ts_start = convert_to_timestamp(start_time, start_date)
        ts_end = convert_to_timestamp('23:59:59', end_date)
        schedule_groups[match_num] = (match_num, ts_start, ts_end)

        has_foundation = bool(row[0])
        away_name = row[3]
        home_name = row[5]
        away_id = franchises[away_name]
        home_id = franchises[home_name]
        # Format: Gamemode,League,Match,Home,Away,Home Franchise ID,Away
        # Franchise ID
        for mode in gamemodes:
            for league in leagues:
                if has_foundation:
                    if league == 'Premier':
                        continue
                else:
                    if league == 'Foundation':
                        continue

                new_row = (mode, league, match_num, home_name, away_name, home_id, away_id)
                matches.append(new_row)
        

print(schedule_groups)
print(matches)

with open('input_data/season_17_mledb_matches.csv', 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['match_number', 'from', 'to', 'season', 'is_double_header'])
    for _,v in schedule_groups.items():
        writer.writerow([*v, '17', 'false'])
    
with open('input_data/season_17_schedule_groups.csv', 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['start', 'end', 'description'])
    for _,v in schedule_groups.items():
        desc = f'Match {v[0]}'
        writer.writerow([v[1], v[2], desc])

with open('input_data/season_17_matches.csv', 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Gamemode','League','Match','Home','Away','Home Franchise ID','Away Franchise ID'])
    for match in matches:
        writer.writerow(match)