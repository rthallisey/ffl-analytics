import player

class Team(object):
    '''Teams are part of the league'''
    def __init__(self, data, request):
        self.request = request
        self.team_id = data['teamId']
        self.team_abbrev = data['teamAbbrev']
        self.name = "%s %s" % (data['teamLocation'], data['teamNickname'])
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
        self.roster = {}
        self._fetch_schedule(data)
        self._fetch_roster()

    def __repr__(self):
        return self.team_name

    def _fetch_roster(self):
        '''Initialize a teams roster with players from the current week'''
        params = {
            'teamIds': [self.team_id],
            'useCurrentPeriodRealStats' : 'true',
            'useCurrentPeriodProjectedStats' : 'true',
        }

        roster = self.request.Get('rosterInfo', params)
        for players in range(len(roster['leagueRosters']['teams'][0]['slots'])):
            p = player.Player(roster['leagueRosters']['teams'][0]['slots'][players])
            name = p.player_name
            self.roster[name] = p

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

    def get_roster(self, week=None):
        '''Get roster for a given week'''
        params = {
            'teamIds': [self.team_id],
            'useCurrentPeriodRealStats' : 'true',
            'useCurrentPeriodProjectedStats' : 'true',
        }

        if week is not None:
            params['scoringPeriodId'] = week

        roster = self.request.Get('rosterInfo', params)

        self.roster = {}
        for players in range(len(roster['leagueRosters']['teams'][0]['slots'])):
            p = player.Player(roster['leagueRosters']['teams'][0]['slots'][players])
            name = p.player_name
            self.roster[name] = p

        return self.roster.values()

    def player_changes(self, start_week, end_week=None):
        '''Count the number of different players from start_week to end_week for
           a team.

           How similar is your current team from the team you drafted.
        '''
        start_roster = self.get_roster(start_week)
        end_roster = self.get_roster(end_week)

        player_count = 0
        for player in start_roster.keys():
            if player in end_roster.keys():
                player_count += 1
        return player_count

    def scoreboard(self, week=None):
        '''Returns a teams matchup for a given week'''
        params = {
            'teamId': self.team_id
        }
        if week is not None:
            params['matchupPeriodId'] = week

        scoreboard_data = self.request.Get('scoreboard', params)

        print scoreboard_data
        score = {}
        fn = scoreboard_data['scoreboard']['matchups'][0]['teams'][0]['team']['teamLocation']
        ln = scoreboard_data['scoreboard']['matchups'][0]['teams'][0]['team']['teamNickname']
        team1 = "%s %s" % (fn, ln)
        score[team1] = scoreboard_data['scoreboard']['matchups'][0]['teams'][0]['score']

        fn = scoreboard_data['scoreboard']['matchups'][0]['teams'][1]['team']['teamLocation']
        ln = scoreboard_data['scoreboard']['matchups'][0]['teams'][1]['team']['teamNickname']
        team2 = "%s %s" % (fn, ln)
        score[team2] = scoreboard_data['scoreboard']['matchups'][0]['teams'][1]['score']

        return score

    def players(self, roster=None, week=None):
        '''Returns a dict with player names as keys and player ids as values'''
        if roster is None:
            roster = self.get_roster(week)

        players = {}
        for player in roster:
            players[player.player_name] = player.player_id

        return players
