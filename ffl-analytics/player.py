class Player(object):
    def __init__(self, roster):
        self.roster_ids = {0:'QB', 2:'RB', 4:'WR', 6:'TE', 23:'FLEX', 16:'D/ST', 17:'K', 20:'Bench'}
        self.position = self.roster_ids[roster['slotCategoryId']]
        self.player_name = "%s %s" %(roster['player']['firstName'], roster['player']['lastName'])

    def __repr__(self):
        return self.player_name

    def get_name(self):
        return self.player_name

    def get_position(self):
        return self.position
