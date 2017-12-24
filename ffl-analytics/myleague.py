#!/usr/bin/env python

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(
        os.path.dirname(os.path.realpath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import league

league_id = 361793
season_id = 2017
L = league.League(league_id, season_id)
print L

teams = L.teams

camNewton = L.get_player("Cam Newton")
print camNewton.projected_score

fitz = teams[8]
print fitz.get_roster(1)
print fitz.get_roster()

for team in teams:
    print team.players()
    print team.scoreboard()
    print team.player_changes(1)
