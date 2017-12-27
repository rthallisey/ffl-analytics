#!/usr/bin/env python

import sys
import os

import plotly.offline as offline
import plotly.graph_objs as go
import numpy as np

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

player_changes = {}
bench = []
best_player = []
best_player_score = []
team_names = []
avg_points = []
for team in teams.values():
    # Need a better way to get team names in a list
    # __str__ and __repr__ aren't working
    # Nees team names in the same order as players
    team_names.append(team.name)
    best_player.append(team.best_player[0])
    best_player_score.append(team.best_player[1])

    player_changes[team.name] = team.player_changes(1)
    points = []
    for week in range(1,16):
        points.append(round(team.bench_points(week), 1))

    bench.append(go.Scatter(
        x = range(1,16),
        y = points,
        mode = 'lines+markers',
        name = team.name,
    ))

    team.get_avg_player_score(16)
    avg_points.append(go.Scatter(
        x = team.average_player_score.keys(),
        y = team.average_player_score.values(),
        mode = 'lines+markers',
        name = team.name,
    ))


offline.plot({'data': bench,
             'layout': {'title': 'Number of Weekly Bench Points Scored',
                        'font': dict(size=16)}},
             filename='weekly-bench-points.html',
)

offline.plot({'data': avg_points,
             'layout': {'title': 'Average Points Per Position',
                        'font': dict(size=16)}},
             filename='avg-points-position.html',
)

L.get_season_bench_points()
pts = L.season_bench_points
season_bench_points = [go.Bar(x=pts.keys(),
                              y=pts.values()
)]

offline.plot({'data': season_bench_points,
             'layout': {'title': 'Total Bench Points',
                        'font': dict(size=16)}},
             filename='season-bench-points.html',
)

best_players = [go.Bar(x=team_names,
                       y=best_player_score,
                       text=best_player,
)]

offline.plot({'data': best_players,
              'layout': {'title': 'Most Points From A Player',
                         'font': dict(size=16)}},
             filename='most-points-from-players.html',
)

remaining_drafted_players = [go.Bar(y=player_changes.values(),
                                    x=player_changes.keys()
)]

offline.plot({'data': remaining_drafted_players,
             'layout': {'title': 'Number of Remaining Drafted Players',
                        'font': dict(size=16)}},
             filename='remaining-drafted-players.html',
)
