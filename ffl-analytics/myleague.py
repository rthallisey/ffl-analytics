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
season_length = 16
L = league.League(league_id, season_id, season_length)
print L

teams = L.teams

pos_avg = L.get_league_avg_points_per_position()

player_changes = {}
bench = []
best_player = []
best_player_score = []
team_names = []
avg_points = []
scoreboards = {}

mvp = []
new_points = []
old_points = []
opponents_points = []
for team in teams.values():
    # Need a better way to get team names in a list
    # __str__ and __repr__ aren't working
    # Nees team names in the same order as players
    team_names.append(team.name)
    best_player.append(team.best_player['player'])
    best_player_score.append(team.best_player['total_points'])
    print team.best_player['player']

    mvp = []
    new_points = []
    old_points = []
    opponents_points = []

    player_changes[team.name] = team.player_changes(1)
    points = []

    '''
    Get a team's game score
    See if the team won or lost
    Get team's best player name
    Get points scored each game by the best player
    Replace points scored by best player with points score by avg rostered at the same position
    See if new score results in a win or a loss
    '''
    for week in range(1,17):
        points.append(round(team.bench_points(week), 1))

        team.get_best_player_points(week)
        real_scoreboard = team.scoreboard(week)
        adjusted_scoreboard = team.scoreboard(week)

        # Loop isn't zero'd so subtract 1 from week
        difference = real_scoreboard[team.name] - team.best_player['weekly_points'][week-1]
        new_score = difference + pos_avg[team.best_player['position']]
        adjusted_scoreboard[team.name] = new_score

        for t in adjusted_scoreboard.keys():
            if team.name == t:
                pass
            elif t in str(teams.values()):
                opponents_points.append(adjusted_scoreboard[t])
                if new_score > adjusted_scoreboard[t]:
                    adjusted_scoreboard['win'] = True
                else:
                    adjusted_scoreboard['win'] = False

        if team not in scoreboards:
            scoreboards[team] = {}
        scoreboards[team][week] = {'before': real_scoreboard, 'after': adjusted_scoreboard}
        new_points.append(new_score)
        old_points.append(real_scoreboard[team.name])

    bench.append(go.Scatter(
        x = range(1,17),
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

    # Show how important a team's best player was
    mvp.append(go.Scatter(
        x = range(1,17),
        y = opponents_points,
        mode = 'lines+markers',
        name = "Opponent's Score",
    ))

    mvp.append(go.Scatter(
        x = range(1,17),
        y = new_points,
        mode = 'lines+markers',
        name = 'With a %s scoring the position average' % team.best_player['position'],
    ))

    mvp.append(go.Scatter(
        x = range(1,17),
        y = old_points,
        mode = 'lines+markers',
        name = 'With %s' % team.best_player['player'],
    ))

    offline.plot({'data': mvp,
                  'layout': {'title': 'Life Without Your Best Player',
                             'font': dict(size=16)}},
                 filename='best-to-avg-%s.html' % team.name,
    )

offline.plot({'data': bench,
             'layout': {'title': 'Weekly Bench Points Scored',
                        'font': dict(size=16)}},
             filename='weekly-bench-points.html',
)

offline.plot({'data': avg_points,
             'layout': {'title': 'Average Weekly Points Per Position from an Active Roster',
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
              'layout': {'title': 'Most Points from a Player from an Active Roster',
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
