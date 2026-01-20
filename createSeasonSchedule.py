from sqlalchemy import create_engine, text
from database import objects
from datetime import datetime
import os
import csv
from typing import Dict, List, Tuple, NamedTuple
from dataclasses import dataclass

@dataclass
class MatchWeek:
    match_number: int
    start_date: str
    end_date: str
    matches: List[Tuple[str, str, bool]]  # (home, away, has_pl)

    mseason_id: int
    sseason_id: int
    week_refs: List[Tuple[int, int]]  # List of (mmatch_id, sgroup_id)
    fixture_refs: Dict[str, Dict]  # Key: f"{home_team}_{away_team}", Value: dict of ids

class SeasonScheduleCreator:
    def __init__(self, engine, dry_run=False):
        self.game_modes = [13, 14]
        
    def load_franchise_mappings(self):
        query = """
            SELECT f.id, fp.title 
            FROM sprocket.franchise f
            JOIN sprocket.franchise_profile fp ON fp."franchiseId" = f.id
        """
        with self.engine.connect() as conn:
                result = conn.execute(text(query))
                    self.franchise_name_to_id[row[1]] = row[0]

    def parse_csv(self, filepath: str) -> List[MatchWeek]:
        match_weeks: Dict[int, MatchWeek] = {}
        
        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                match_num = int(row['Match #'])
                if match_num not in match_weeks:
                    match_weeks[match_num] = MatchWeek(
                        match_number=match_num,
                        start_date=datetime.strptime(row['Start'], '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S -0700'),
                        end_date=datetime.strptime(row['End'], '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S -0700'),
                        matches=[]
                )
                match_weeks[match_num].matches.append((row['Home'], row['Away'], row['Has_PL']))
        
        return list(match_weeks.values())

    def create_season(self, match_weeks: List[MatchWeek]) -> Tuple[int, int]:
        season_start = match_weeks[0].start_date
        season_end = match_weeks[-1].end_date
        
        mseason = objects.mSeason(
            seasonNumber=19,
            start=season_start,
            end=season_end
        )
        
        sseason = objects.sScheduleGroup(
            start=season_start,
            end=season_end,
            description=f"Season 19",
            typeId=1,
            gameId=7,
            parentGroupId=None
        )
        
        if self.dry_run:
            print("Would execute:")
            print(mseason.query())
            print(sseason.query())
            return (-1, -1)
        
        with self.engine.connect() as conn:
            mseason_result = conn.execute(text(mseason.query()))
            sseason_result = conn.execute(text(sseason.query()))
            mseason_id = mseason_result.fetchone()[0]
            sseason_id = sseason_result.fetchone()[0]

            if not self.dry_run:
                conn.commit()

            return mseason_id, sseason_id

    def create_match_weeks(self, match_weeks: List[MatchWeek], mseason_id: int, sseason_id: int) -> List[Tuple[int, int]]:
        week_ids = []
        
        for week in match_weeks:
            mmatch = objects.mMatch(
                from_date=week.start_date,
                to_date=week.end_date,
                season=18,
                match_number=week.match_number
            )
            
            sgroup = objects.sScheduleGroup(
                start=week.start_date,
                end=week.end_date,
                description=f"Week {week.match_number}",
                typeId=3,
                gameId=7,
                parentGroupId=sseason_id
            )
            
            if self.dry_run:
                print(f"Would create week {week.match_number}:")
                print(mmatch.query())
                print(sgroup.query())
                continue
                
            with self.engine.connect() as conn:
                mmatch_result = conn.execute(text(mmatch.query()))
                sgroup_result = conn.execute(text(sgroup.query()))
                week_ids.append((mmatch_result.fetchone()[0], sgroup_result.fetchone()[0]))
                
                conn.commit()
        return week_ids

    def create_fixtures(self, match_weeks: List[MatchWeek], week_ids: List[Tuple[int, int]]):
        for week, (mmatch_id, sgroup_id) in zip(match_weeks, week_ids):
            print(f'Creating fixtures for week {week.match_number}')
            fixtures_to_create = []
            
            for home_team, away_team in week.matches:
                home_id = self.franchise_name_to_id[home_team]
                away_id = self.franchise_name_to_id[away_team]
                has_pl = any(m.matches for m in week.matches if m[0] == home_team and getattr(m, 'Has_PL', 'FALSE').upper() == 'TRUE')
                
                fixture = {
                    'schedule_group_id': sgroup_id,
                    'home_franchise_id': home_id,
                    'away_franchise_id': away_id,
                    'home_name': home_team,
                    'away_name': away_team,
                    'match_id': mmatch_id,
                    'has_pl': has_pl
                }
                fixtures_to_create.append(fixture)
            
            if self.dry_run:
                print(f"Would create fixtures and matches for week {week.match_number}")
                continue

            self.batch_create_fixtures(fixtures_to_create)

    def batch_create_fixtures(self, fixtures):
        with self.engine.connect() as conn:
            sprocket_fixtures = []
            for f in fixtures:
                sprocket_fixture = objects.sScheduleFixture(
                    scheduleGroupId=f['schedule_group_id'],
                    homeFranchiseId=f['home_franchise_id'],
                    awayFranchiseId=f['away_franchise_id']
                )
                result = conn.execute(text(sprocket_fixture.query()))
                sprocket_fixture_id = result.fetchone()[0]
                f['sprocket_fixture_id'] = sprocket_fixture_id
                
            if not self.dry_run:
                conn.commit()

            mle_fixtures = []
            for f in fixtures:
                mle_fixture = objects.mFixture(
                    match_id=f['match_id'],
                    home_name=f['home_name'],
                    away_name=f['away_name']
                )
                result = conn.execute(text(mle_fixture.query()))
                mle_fixture_id = result.fetchone()[0]
                f['mle_fixture_id'] = mle_fixture_id

                bridge = objects.mbFixtures(
                    mleFixtureId=mle_fixture_id,
                    sprocketFixtureId=f['sprocket_fixture_id']
                )
                conn.execute(text(bridge.query()))

            if not self.dry_run:
                conn.commit()

            for f in fixtures:
                skill_groups = [1, 2, 3, 4] if f['has_pl'] else [2, 3, 4, 5]
                
                match_parent = objects.sMatchParent(fixtureId=f['sprocket_fixture_id'])
                result = conn.execute(text(match_parent.query()))
                match_parent_id = result.fetchone()[0]
                
                if not self.dry_run:
                    conn.commit()

                match_queries = []
                series_queries = []
                
                for skill_group in skill_groups:
                    for game_mode in self.game_modes:
                        match = objects.sMatch(
                            skillGroupId=skill_group,
                            matchParentId=match_parent_id,
                            gameModeId=game_mode
                        )
                        match_queries.append(match.query())
                        
                        league_map = {
                            1: 'PREMIER',
                            2: 'MASTER',
                            3: 'CHAMPION',
                            4: 'ACADEMY',
                            5: 'FOUNDATION'
                        }
                        mode_map = {
                            13: 'DOUBLES',
                            14: 'STANDARD'
                        }
                        
                        series = objects.mSeries(
                            league=league_map[skill_group],
                            mode=mode_map[game_mode],
                            fixture_id=f['mle_fixture_id']
                        )
                        series_queries.append(series.query())
                
                for query in match_queries:
                    conn.execute(text(query))
                for query in series_queries:
                    conn.execute(text(query))

            if not self.dry_run:
                conn.commit()

    def create_schedule(self, csv_path: str):
        self.load_franchise_mappings()
        match_weeks = self.parse_csv(csv_path)

        if self.dry_run:
            print("Would execute the following queries:")
            self.generate_queries(match_weeks)
            return

        with self.engine.connect() as conn:
            try:
                refs = self.create_all_objects(conn, match_weeks)
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

    def generate_queries(self, match_weeks: List[MatchWeek]):
        """Print all queries that would be executed (dry run mode)"""
        # Season containers
        season_start = match_weeks[0].start_date
        season_end = match_weeks[-1].end_date
        
        mseason = objects.mSeason(
            seasonNumber=18,
            start=season_start,
            end=season_end
        )
        print("Create mledb season:")
        print(mseason.query())
        
        sseason = objects.sScheduleGroup(
            end=season_end,
            description="Season 18",
            typeId=1,
            gameId=7,
            parentGroupId=None
        )
        print("\nCreate sprocket season group:")
        print(sseason.query())
        
        # Match weeks
        print("\nCreate match weeks:")
        for week in match_weeks:
            mmatch = objects.mMatch(
                from_date=week.start_date,
                to_date=week.end_date,
                season=18,
                match_number=week.match_number
            )
            print(f"\nWeek {week.match_number} mledb match:")
            
            sgroup = objects.sScheduleGroup(
                start=week.start_date,
                end=week.end_date,
                description=f"Week {week.match_number}",
                typeId=3,
                gameId=7,
                parentGroupId=-1  # Would be sseason_id
            )
            print(f"Week {week.match_number} sprocket group:")
            print(sgroup.query())
            
            # Fixtures and matches
            for home, away, has_pl in week.matches:
                print(f"\nFixtures for {home} vs {away}:")
                sprocket_fixture = objects.sScheduleFixture(
                    homeFranchiseId=self.franchise_name_to_id[home],
                    awayFranchiseId=self.franchise_name_to_id[away]
                )
                print(sprocket_fixture.query())
                
                mle_fixture = objects.mFixture(
                    match_id=-1,  # Would be mmatch_id
                    home_name=home,
                    away_name=away
                print(mle_fixture.query())
                
                print("\nBridge, matches, and series would be created...")

    def create_all_objects(self, conn, match_weeks: List[MatchWeek]) -> ScheduleReferences:
        """Create all objects in a single transaction, maintaining references"""
        refs = {}
        # Create season containers
        season_start = match_weeks[0].start_date
        season_end = match_weeks[-1].end_date
        
        mseason = objects.mSeason(
            seasonNumber=18,
            start=season_start,
            end=season_end
        )
        result = conn.execute(text(mseason.query()))
        mseason_id = result.fetchone()[0]
        
        sseason = objects.sScheduleGroup(
            start=season_start,
            end=season_end,
        mseason = objects.mSeason(
            seasonNumber=18,
            start=season_start,
            end=season_end
        )
        result = conn.execute(text(sseason.query()))
        sseason_id = result.fetchone()[0]
        
        # Create match weeks
        week_refs = []
        for week in match_weeks:
            mmatch = objects.mMatch(
                from_date=week.start_date,
                to_date=week.end_date,
                season=18,
                match_number=week.match_number
            )
            result = conn.execute(text(mmatch.query()))
            mmatch_id = result.fetchone()[0]
        # Create match weeks
            sgroup = objects.sScheduleGroup(
                start=week.start_date,
                end=week.end_date,
                description=f"Week {week.match_number}",
                typeId=3,
                gameId=7,
                parentGroupId=sseason_id
            )
            result = conn.execute(text(sgroup.query()))
            sgroup_id = result.fetchone()[0]
            
            week_refs.append((mmatch_id, sgroup_id))

                end=week.end_date,
            for home, away, has_pl in week.matches:
                fixture_key = f"{home}_{away}"
                refs[fixture_key] = {}
                
                # Create sprocket fixture
                sprocket_fixture = objects.sScheduleFixture(
                    scheduleGroupId=sgroup_id,
                    homeFranchiseId=self.franchise_name_to_id[home],
                    awayFranchiseId=self.franchise_name_to_id[away]
                )
            # Create fixtures and related objects
                sprocket_fixture_id = result.fetchone()[0]
                refs[fixture_key]['sprocket_fixture_id'] = sprocket_fixture_id
                
                # Create mledb fixture
                # Create sprocket fixture
                    match_id=mmatch_id,
                    home_name=home,
                    away_name=away
                )
                result = conn.execute(text(mle_fixture.query()))
                mle_fixture_id = result.fetchone()[0]
                refs[fixture_key]['mle_fixture_id'] = mle_fixture_id
                
                # Create bridge
                bridge = objects.mbFixtures(
                    mleFixtureId=mle_fixture_id,
                    sprocketFixtureId=sprocket_fixture_id
                )
                conn.execute(text(bridge.query()))
                
                # Create matches and series
                skill_groups = [1, 2, 3, 4] if has_pl.upper() == 'TRUE' else [2, 3, 4, 5]
                league_map = {
                    1: 'PREMIER', 2: 'MASTER', 3: 'CHAMPION',
                    4: 'ACADEMY', 5: 'FOUNDATION'
                }
                mode_map = {13: 'DOUBLES', 14: 'STANDARD'}
                
                for skill_group in skill_groups:
                    for game_mode in self.game_modes:
                        # Create match parent for this specific match
                        match_parent = objects.sMatchParent(fixtureId=sprocket_fixture_id)
                        result = conn.execute(text(match_parent.query()))
                        match_parent_id = result.fetchone()[0]
                        
                        # Create sprocket match
                            skillGroupId=skill_group,
                            matchParentId=match_parent_id,
                            gameModeId=game_mode
                        )
                        conn.execute(text(match.query()))
                        
                        # Create mledb series
                        series = objects.mSeries(
                            league=league_map[skill_group],
                            mode=mode_map[game_mode],
                            fixture_id=mle_fixture_id
                        )
                        conn.execute(text(series.query()))
        
        return ScheduleReferences(mseason_id, sseason_id, week_refs, refs)

if __name__ == '__main__':
    username = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    hostname = os.environ.get('DB_HOST')
    port = os.environ.get('DB_PORT')
    database = os.environ.get('DB_NAME')

    connstr = f'postgresql+psycopg2://{username}:{password}@{hostname}:{port}/{database}'
    engine = create_engine(connstr)
    creator = SeasonScheduleCreator(engine, dry_run=False)
    creator.create_schedule('inputs/s19_schedule.csv')