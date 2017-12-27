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
bench = {}
for team in teams.values():
    player_changes[team.name] = team.player_changes(1)

    points = []
    for week in range(1,16):
        points.append(round(team.bench_points(week), 1))

    bench[team.name] = go.Scatter(
        x = range(1,16),
        y = points,
        mode = 'lines+markers',
        name = team.name,
    )

weekly_bench_points = bench.values()
offline.plot({'data': weekly_bench_points,
             'layout': {'title': 'Number of Weekly Bench Points Scored',
                        'font': dict(size=16)}},
             filename='weekly-bench-points.html',
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

remaining_drafted_players = [go.Bar(y=player_changes.values(),
                                    x=player_changes.keys()
)]

offline.plot({'data': remaining_drafted_players,
             'layout': {'title': 'Number of Remaining Drafted Players',
                        'font': dict(size=16)}},
             filename='remaining-drafted-players.html',
)
