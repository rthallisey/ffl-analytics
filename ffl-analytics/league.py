import request
from utils import (two_step_dominance,
                    power_points, )
from team import Team
from settings import Settings
from matchup import Matchup

class League(object):
    '''Creates a League instance for Public ESPN league'''
    def __init__(self, league_id, year, espn_s2=None, swid=None):
        self.request = request.Request(league_id, year)

        self.league_id = league_id
        self.year = year
        self.teams = []
        self.espn_s2 = espn_s2
        self.swid = swid
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

        for team in teams:
            self.teams.append(Team(teams[team], self.request))

        # replace opponentIds in schedule with team instances
        for team in self.teams:
            for week, matchup in enumerate(team.schedule):
                for opponent in self.teams:
                    if matchup == opponent.team_id:
                        team.schedule[week] = opponent

        # calculate margin of victory
        for team in self.teams:
            for week, opponent in enumerate(team.schedule):
                mov = team.scores[week] - opponent.scores[week]
                team.mov.append(mov)

        # sort by team ID
        self.teams = sorted(self.teams, key=lambda x: x.team_id, reverse=False)

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
        print "Teams in this league are %s" % self.teams
        return None

    def get_player(self, player):
        for team in self.teams:
            print team.roster.keys()
            if player in team.roster.keys():
                return team.roster[player]
