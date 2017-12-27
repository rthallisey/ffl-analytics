import request
from utils import (two_step_dominance,
                    power_points, )
from team import Team
from settings import Settings
from matchup import Matchup
from cache import Cache

class League(object):
    '''Creates a League instance for Public ESPN league'''
    def __init__(self, league_id, year, espn_s2=None, swid=None):
        self.request = request.Request(league_id, year)

        self.league_id = league_id
        self.year = year
        self.teams = {}
        self.espn_s2 = espn_s2
        self.swid = swid
        self.season_bench_points = {}
        self._fetch_league()

    def __repr__(self):
        return 'League(%s, %s)' % (self.league_id, self.year, )

    def _fetch_league(self):
        league_data = self.request.Get('leagueSettings')
        self._fetch_teams(league_data)
        self._fetch_settings(league_data)

    def _fetch_teams(self, data):
        '''Fetch teams in league'''
        teams = data['leaguesettings']['teams']
        team_ids = str(teams.keys()).replace("[", "").replace("]", "").replace(" ", "").replace("u", "").replace("'", "")

        for team in teams:
            t = Team(teams[team], self.request)
            self.teams[t.team_id] = t

        self._fetch_rosters(team_ids)

        # replace opponentIds in schedule with team instances
        for team in self.teams.values():
            for week, matchup in enumerate(team.schedule):
                for opponent in self.teams.values():
                    if matchup == opponent.team_id:
                        team.schedule[week] = opponent

        # calculate margin of victory
        for team in self.teams.values():
            for week, opponent in enumerate(team.schedule):
                mov = team.scores[week] - opponent.scores[week]
                team.mov.append(mov)

    def _fetch_rosters(self, team_ids):
        params = {
            'teamIds': team_ids,
            'useCurrentPeriodRealStats' : 'true',
            'useCurrentPeriodProjectedStats' : 'true',
        }

        # Create a new set a cached data by combining the newest data with
        # the already cached data in 'new_cached_data'.
        new_cached_data = {}

        roster = self.request.Get('rosterInfo', params)
        week = roster['leagueRosters']['scoringPeriodId']
        self.current_week = week

        # Search from the current week back to the start of the season
        # or the latest cached week.
        #
        # Cache everything except the current week since it likely to change.
        #
        cached = Cache(self.league_id, self.year)

        # We always want to gather the current week since it's never cached
        print "Gathering week %s data..." % week
        params['scoringPeriodId'] = week
        roster = self.request.Get('rosterInfo', params)

        for week in range(week, cached.cached_week, -1):
            for t in range(len(roster['leagueRosters']['teams'])):
                id = roster['leagueRosters']['teams'][t]['teamId']
                self.teams[id].fetch_weekly_roster(roster['leagueRosters']['teams'][t], week)

            print "Gathering week %s data..." % week
            params['scoringPeriodId'] = week
            roster = self.request.Get('rosterInfo', params)
            new_cached_data[week] = roster

        # Translate the cached 'team_data' keys into ints. Then reverse sort
        # them and translate them back to strings.
        #
        # There's probably a better way to get reverse list order.
        #
        try:
            cached_data = sorted([int(x) for x in cached.cached_data['team_data'].keys()], reverse=True)
        except:
            cached_data = []
        for week in cached_data:
            for t in range(len(cached.cached_data['team_data'][str(week)]['leagueRosters']['teams'])):
                id = cached.cached_data['team_data'][str(week)]['leagueRosters']['teams'][t]['teamId']
                self.teams[id].fetch_weekly_roster(cached.cached_data['team_data'][str(week)]['leagueRosters']['teams'][t], week)
            print "Using cached week %s data." % week
            new_cached_data[str(week)] = cached.cached_data['team_data'][str(week)]

        # Cache new data
        cached.cache_data(new_cached_data, self.current_week)

    def _fetch_settings(self, data):
        self.settings = Settings(data)

    def power_rankings(self, week):
        '''Return power rankings for any week'''

        # calculate win for every week
        win_matrix = []
        teams_sorted = sorted(self.teams, key=lambda x: x.team_id,
                              reverse=False)

        for team in teams_sorted:
            wins = [0]*32
            for mov, opponent in zip(team.mov[:week], team.schedule[:week]):
                opp = int(opponent.team_id)-1
                if mov > 0:
                    wins[opp] += 1
            win_matrix.append(wins)
        dominance_matrix = two_step_dominance(win_matrix)
        power_rank = power_points(dominance_matrix, teams_sorted, week)
        return power_rank

    def get_team(self, name):
        for team in range(len(self.teams)):
            if team.get_teamname() == name:
                return team
        print "Couldn't find matching team with name %s" % name
        print "Teams in this league are %s" % self.teams.values()
        return None

    def get_player(self, player):
        for team in self.teams.values():
            if player in team.roster.keys():
                return team.roster[player]

    def get_bench_points(self, week=None):
        for team in self.teams.values():
            points = team.bench_points(week)
            if team.name in self.season_bench_points:
                self.season_bench_points[team.name] += points
            else:
                self.season_bench_points[team.name] = points

    def get_season_bench_points(self):
        # Weeks 1-15
        for week in range(1,16):
            self.get_bench_points(week)

        return sorted(self.season_bench_points.iteritems(), key=lambda p: p[1])
