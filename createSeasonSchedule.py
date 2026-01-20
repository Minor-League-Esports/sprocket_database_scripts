from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import objects
from datetime import datetime
import os
import csv
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class MatchWeek:
    match_number: int
    start_date: datetime
    end_date: datetime
    matches: List[Tuple[str, str, str]]  # (home, away, has_pl)

class SeasonScheduleCreator:
    def __init__(self, engine, dry_run=False):
        self.engine = engine
        self.dry_run = dry_run
        self.Session = sessionmaker(bind=self.engine)
        self.franchise_name_to_id = {}
        self.game_modes = [13, 14]
        self.season_number = 19

    def load_franchise_mappings(self):
        query = """
            SELECT fp.title, f.id
            FROM sprocket.franchise f
            JOIN sprocket.franchise_profile fp ON fp."franchiseId" = f.id
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            for row in result:
                self.franchise_name_to_id[row[0]] = row[1]

    def parse_csv(self, filepath: str) -> List[MatchWeek]:
        match_weeks: Dict[int, MatchWeek] = {}
        
        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                match_num = int(row['Match #'])
                if match_num not in match_weeks:
                    match_weeks[match_num] = MatchWeek(
                        match_number=match_num,
                        start_date=datetime.strptime(row['Start'], '%m/%d/%Y %H:%M:%S'),
                        end_date=datetime.strptime(row['End'], '%m/%d/%Y %H:%M:%S'),
                        matches=[]
                    )
                match_weeks[match_num].matches.append((row['Home'], row['Away'], row['Has_PL']))
        
        return list(match_weeks.values())

    def create_schedule(self, csv_path: str):
        self.load_franchise_mappings()
        match_weeks = self.parse_csv(csv_path)

        session = self.Session()
        try:
            self.create_all_objects(session, match_weeks)
            if self.dry_run:
                print("Dry run: Rolling back changes.")
                session.rollback()
            else:
                session.commit()
                print("Schedule created successfully.")
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def create_all_objects(self, session, match_weeks: List[MatchWeek]):
        """Create all objects in a single transaction"""
        if not match_weeks:
            return

        season_start = match_weeks[0].start_date
        season_end = match_weeks[-1].end_date
        
        # Create season containers
        print(f"Creating Season {self.season_number}...")
        
        # Check if mSeason exists
        mseason = session.query(objects.mSeason).filter_by(season_number=self.season_number).first()
        if not mseason:
            mseason = objects.mSeason(
                season_number=self.season_number,
                start_date=season_start,
                end_date=season_end
            )
            session.add(mseason)
            session.flush() # To get ID if needed, though PK is season_number
        
        sseason = objects.sScheduleGroup(
            start=season_start,
            end=season_end,
            description=f"Season {self.season_number}",
            typeId=1,
            gameId=7,
            parentGroupId=None
        )
        session.add(sseason)
        session.flush()
        sseason_id = sseason.id

        # Create match weeks
        for week in match_weeks:
            print(f"Processing Week {week.match_number}...")
            
            mmatch = objects.mMatch(
                from_date=week.start_date,
                to_date=week.end_date,
                season=self.season_number,
                match_number=week.match_number,
                is_double_header=False # Default
            )
            session.add(mmatch)
            session.flush()
            mmatch_id = mmatch.id
            
            sgroup = objects.sScheduleGroup(
                start=week.start_date,
                end=week.end_date,
                description=f"Week {week.match_number}",
                typeId=3,
                gameId=7,
                parentGroupId=sseason_id
            )
            session.add(sgroup)
            session.flush()
            sgroup_id = sgroup.id

            # Create bridge between week and schedule group
            week_bridge = objects.mbMatchToScheduleGroup(
                matchId=mmatch_id,
                weekScheduleGroupId=sgroup_id
            )
            session.add(week_bridge)
            
            # Create fixtures and matches
            for home, away, has_pl_str in week.matches:
                has_pl = has_pl_str.upper() == 'TRUE'
                
                # Create sprocket fixture
                sprocket_fixture = objects.sScheduleFixture(
                    scheduleGroupId=sgroup_id,
                    homeFranchiseId=self.franchise_name_to_id[home],
                    awayFranchiseId=self.franchise_name_to_id[away]
                )
                session.add(sprocket_fixture)
                session.flush()
                sprocket_fixture_id = sprocket_fixture.id
                
                # Create mledb fixture
                mle_fixture = objects.mFixture(
                    match_id=mmatch_id,
                    home_name=home,
                    away_name=away
                )
                session.add(mle_fixture)
                session.flush()
                mle_fixture_id = mle_fixture.id
                
                # Create bridge
                bridge = objects.mbFixtures(
                    mleFixtureId=mle_fixture_id,
                    sprocketFixtureId=sprocket_fixture_id
                )
                session.add(bridge)
                
                # Create matches and series
                skill_groups = [1, 2, 3, 4] if has_pl else [2, 3, 4, 5]
                league_map = {
                    1: 'PREMIER', 2: 'MASTER', 3: 'CHAMPION',
                    4: 'ACADEMY', 5: 'FOUNDATION'
                }
                mode_map = {13: 'DOUBLES', 14: 'STANDARD'}
                
                for skill_group in skill_groups:
                    for game_mode in self.game_modes:
                        # Create match parent for this specific match
                        match_parent = objects.sMatchParent(fixtureId=sprocket_fixture_id)
                        session.add(match_parent)
                        session.flush()
                        match_parent_id = match_parent.id
                        
                        # Create sprocket match
                        match = objects.sMatch(
                            skillGroupId=skill_group,
                            matchParentId=match_parent_id,
                            gameModeId=game_mode
                        )
                        session.add(match)
                        
                        # Create mledb series
                        series = objects.mSeries(
                            league=league_map[skill_group],
                            mode=mode_map[game_mode],
                            fixture_id=mle_fixture_id
                        )
                        session.add(series)

if __name__ == '__main__':
    username = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    hostname = os.environ.get('DB_HOST')
    port = os.environ.get('DB_PORT')
    database = os.environ.get('DB_NAME')

    if not all([username, password, hostname, port, database]):
        print("Missing database environment variables.")
        exit(1)

    connstr = f'postgresql+psycopg2://{username}:{password}@{hostname}:{port}/{database}'
    engine = create_engine(connstr)
    creator = SeasonScheduleCreator(engine, dry_run=True)
    creator.create_schedule('inputs/s19_schedule.csv')
