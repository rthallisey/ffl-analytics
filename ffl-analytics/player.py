class Player(object):
    def __init__(self, roster):
        self.roster_ids = {0:'QB', 2:'RB', 4:'WR', 6:'TE', 23:'FLEX', 16:'D/ST', 17:'K', 20:'Bench'}
        self.position = self.roster_ids[roster['slotCategoryId']]

        try:
            self.player_name = "%s %s" %(roster['player']['firstName'], roster['player']['lastName'])
            self.player_id = roster['player']['playerId']

            if 'appliedStatTotal' in roster['currentPeriodRealStats']:
                self.player_score = round(roster['currentPeriodRealStats']['appliedStatTotal'], 1)
            else:
                self.player_score = 0

            if 'appliedStatTotal' in roster['currentPeriodProjectedStats']:
                self.projected_score = round(roster['currentPeriodProjectedStats']['appliedStatTotal'], 1)

        except KeyError:
            self.player_name = "Empty"
            self.player_id = 0
            self.player_score = 0
            self.projected_score = 0

    def __repr__(self):
        return self.player_name

    def is_benched(self):
        '''Return true if a player is on the bench'''
        if self.position == 'Bench':
            return True
        return False
