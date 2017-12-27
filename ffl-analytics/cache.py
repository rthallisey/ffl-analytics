import os
import json

class Cache(object):
    '''Cache team data for a league'''
    def __init__(self, league_id, year):
        self.cache_file = "%s-ffl-%s.data" % (year, league_id)
        self.cached_data = {}

        if os.path.isfile(self.cache_file):
            print "Using cached file %s" % self.cache_file
            self._setup_cache()
        else:
            print "No cache found"
            # 0 is Week 1
            self.cached_week = 0

    def _setup_cache(self):
        with open(self.cache_file, 'r') as cache:
            data = json.loads(cache.read())
            self.cached_week = data['week']
            self.cached_data = data

    def cache_data(self, data, week):
        if os.path.isfile(self.cache_file):
            os.remove(self.cache_file)

        with open(self.cache_file, 'w') as cache:
            self.cached_data['team_data'] = data
            self.cached_data['week'] = week
            json.dump(self.cached_data, cache)
