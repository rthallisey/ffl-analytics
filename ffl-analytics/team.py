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

        self.season_bench_points = 0
        self.best_player = ()
        self.average_player_score = {}
        self.player_scores = {'RB': {}, 'WR': {}, 'QB': {}, 'TE': {}, 'K': {}, 'D/ST': {}, 'Empty': {}}

        self._fetch_schedule(data)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

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

    def _fetch_player_scores(self, player):
        if player.name in self.player_scores[player.position].keys():
            score = self.player_scores[player.position][player.name]
            if not player.is_benched():
                score += player.player_score
            self.player_scores[player.position][player.name] = score
        else:
            if not player.is_benched():
                self.player_scores[player.position][player.name] = player.player_score
            else:
                self.player_scores[player.position][player.name] = 0

    def _fetch_best_player(self, player):
        if self.best_player == ():
            self.best_player = (player.name, player.player_score)
        elif self.best_player[1] < self.player_scores[player.position][player.name]:
            self.best_player = (player.name, self.player_scores[player.position][player.name])

    def fetch_weekly_roster(self, roster, week):
        '''Initialize a teams roster with players from the every week'''
        player_dict = {}
        for players in range(len(roster['slots'])):
            p = player.Player(roster['slots'][players])
            name = p.name
            player_dict[name] = p
            self.roster[week] = player_dict

            self._fetch_player_scores(p)
            self._fetch_best_player(p)

    def get_avg_player_score(self, num_weeks):
        for position in self.player_scores:
            avg = 0
            for player in self.player_scores[position]:
                avg += self.player_scores[position][player]
            self.average_player_score[position] = avg/num_weeks
        self.average_player_score.pop('Empty', None)
        return self.average_player_score

    def players(self, week=None):
        '''Get roster for a given week'''
        if week is None:
            week = max(self.roster.keys())
        return self.roster[week]

    def player_changes(self, start_week, end_week=None):
        '''Count the number of different players from start_week to end_week for
           a team.

           How similar is your current team from the team you drafted.
        '''
        start_roster = self.players(start_week)
        end_roster = self.players(end_week)

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

    def bench_points(self, week=None):
        '''Return the points scored on the bench from a specific week'''
        score = 0
        for player in self.players(week).values():
            if player.is_benched():
                score += player.player_score
        return score
