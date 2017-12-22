import requests

from exception import (PrivateLeagueException,
                        InvalidLeagueException,
                        UnknownLeagueException, )

class Request(object):
    '''Requests class'''
    def __init__(self, league_id, year, espn_s2=None, swid=None):
        self.api = "http://games.espn.com/ffl/api/v2/"
        self.league_id = league_id
        self.year = year
        self.espn_s2 = espn_s2
        self.swid = swid

        self.params = {
            'leagueId': self.league_id,
            'seasonId': self.year
        }

        self.cookies = None
        if self.espn_s2 and self.swid:
            self.cookies = {
                'espn_s2': self.espn_s2,
                'SWID': self.swid
            }

    def _error_check(self, data, status_code):
        if status_code == 401:
            raise PrivateLeagueException(data['error'][0]['message'])

        elif status_code == 404:
            raise InvalidLeagueException(data['error'][0]['message'])

        elif status_code != 200:
            raise UnknownLeagueException('Unknown %s Error' % status_code)


    def Get(self, url, params=None):
        if params is not None:
            params = dict(params.items() + self.params.items())
        else:
            params = self.params

        r = requests.get('%s%s' %(self.api, url), params, cookies=self.cookies)
        try:
            data = r.json()
        except ValueError:
            print "The url %s%s didn't contain any data" %s(self.api, url)
        self._error_check(data, r.status_code)
        return data
