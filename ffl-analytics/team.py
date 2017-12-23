import player

class Team(object):
    '''Teams are part of the league'''
    def __init__(self, data, request):
        self.request = request
        self.team_id = data['teamId']
        self.team_abbrev = data['teamAbbrev']
        self.team_name = "%s %s" % (data['teamLocation'], data['teamNickname'])
        self.division_id = data['division']['divisionId']
        self.division_name = data['division']['divisionName']
        self.wins = data['record']['overallWins']
        self.losses = data['record']['overallLosses']
        self.points_for = data['record']['pointsFor']
        self.points_against = data['record']['pointsAgainst']
        self.owner = "%s %s" % (data['owners'][0]['firstName'],
                                data['owners'][0]['lastName'])
        self.schedule = []
        self.scores = []
        self.mov = []
        self._fetch_schedule(data)
        self.roster = []

    def __repr__(self):
        return self.team_name

    def _fetch_schedule(self, data):
        '''Fetch schedule and scores for team'''
        matchups = data['scheduleItems']

        for matchup in matchups:
            if not matchup['matchups'][0]['isBye']:
                if matchup['matchups'][0]['awayTeamId'] == self.team_id:
                    score = matchup['matchups'][0]['awayTeamScores'][0]
                    opponentId = matchup['matchups'][0]['homeTeamId']
                else:
                    score = matchup['matchups'][0]['homeTeamScores'][0]
                    opponentId = matchup['matchups'][0]['awayTeamId']
            else:
                score = matchup['matchups'][0]['homeTeamScores'][0]
                opponentId = matchup['matchups'][0]['homeTeamId']

            self.scores.append(score)
            self.schedule.append(opponentId)

    def _add_player(self, player, player_string):
        self.roster.append(player)
        self.roster_strings.append(player_string)

    def get_roster(self, week=None):
        '''Get roster for a given week'''
        params = {
            'teamIds': [self.team_id],
            }

        if week is not None:
            params['scoringPeriodId'] = week

        roster = self.request.Get('rosterInfo', params)

        self.roster = []
        self.roster_strings = []
        for players in range(len(roster['leagueRosters']['teams'][0]['slots'])):
            p = player.Player(roster['leagueRosters']['teams'][0]['slots'][players])
            self._add_player(p, p.get_name())
        return self.roster

    def get_roster_strings(self, week=None):
        self.get_roster(week)
        return self.roster_strings

    def name(self):
        return self.team_name

    def get_teamid(self):
        return self.team_id

    def player_changes(self, start_week, end_week=None):
        '''Count the number of different players from start_week to end_week for
           a team.

           How similar is your current team from the team you drafted.
        '''
        start_roster = self.get_roster_strings(start_week)
        end_roster = self.get_roster_strings(end_week)

        player_count = 0
        for player in start_roster:
            if player in end_roster:
                player_count += 1
        return player_count
