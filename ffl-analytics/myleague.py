#!/usr/bin/env python

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(
        os.path.dirname(os.path.realpath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import league
import plot

league_id = 361793
season_id = 2017
season_length = 16
L = league.League(league_id, season_id, season_length)
print L

teams = L.teams

pos_avg = L.get_league_avg_points_per_position()

plot_data = {
    'name': '',
    'x': list(),
    'y': list(),
    'plot_type': '',
    'text': '',
    'title': '',
    'filename': '',
}

player_changes = {}
best_player = []
best_player_score = []
team_names = []
scoreboards = {}

new_points = []
old_points = []
opponents_points = []
mvp_value = {}

plot_data['filename'] = "weekly-bench-points.html"
plot_data['title'] = "Weekly Bench Points Scored"
BenchPlot = plot.Plot(plot_data)

plot_data['filename'] = "avg-points-position.html"
plot_data['title'] = "Average Weekly Points Per Position from an Active Roster"
Average_points_plot = plot.Plot(plot_data)
for team in teams.values():
    # Need a better way to get team names in a list
    # __str__ and __repr__ aren't working
    # Nees team names in the same order as players
    team_names.append(team.name)
    best_player.append(team.best_player['player'])
    best_player_score.append(team.best_player['total_points'])
    print team.best_player['player']

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

        if team not in mvp_value:
            mvp_value[team] = (0, team.best_player['player'])
        if not real_scoreboard['win'] and adjusted_scoreboard['win']:
            mvp_value[team] = (mvp_value[team][0]-1, team.best_player['player'])
        elif real_scoreboard['win'] and not adjusted_scoreboard['win']:
            # MVP got you x amount of wins vs the avg player at the position
            mvp_value[team] = (mvp_value[team][0]+1, team.best_player['player'])

    BenchPlot.scatter(range(1, 17), points, team.name)

    team.get_avg_player_score(16)
    Average_points_plot.scatter(team.average_player_score.keys(), team.average_player_score.values(), team.name)

    plot_data['filename'] = "best-to-avg-%s.html" % team.name
    plot_data['title'] = "Life Without Your Best Player"
    MVP_plot = plot.Plot(plot_data)
    MVP_plot.scatter(range(1, 17), opponents_points, "Opponent's Score")
    MVP_plot.scatter(range(1, 17), new_points, "With a %s scoring the position average" % team.best_player['position'])
    MVP_plot.scatter(range(1, 17), old_points, "With %s" % team.best_player['player'])
    MVP_plot.plot_offline()
    # MVP_plot.plot()


BenchPlot.plot_offline()
# Benchplot.plot()

Average_points_plot.plot_offline()
# Average_points_plot.plot()

plot_data['filename'] = "team_mvp_value.html"
plot_data['title'] = "Team MVP value"
MVP_win_changes = plot.Plot(plot_data)
MVP_win_changes.bar([str(v) for v in mvp_value.keys()],
                        [v[0] for v in mvp_value.values()],
                        [v[1] for v in mvp_value.values()])
MVP_win_changes.plot_offline()
# MVP_win_changes.plot()

L.get_season_bench_points()
pts = L.season_bench_points
plot_data['filename'] = "season-bench-points.html"
plot_data['title'] = "Total Bench Points"
Season_bench_points = plot.Plot(plot_data)
Season_bench_points.bar(pts.keys(), pts.values())
Season_bench_points.plot_offline()
# Season_bench_points.plot()

plot_data['filename'] = "most-points-from-players.html"
plot_data['title'] = "Most Points from a Player from an Active Roster"
Season_bench_points = plot.Plot(plot_data)
Season_bench_points.bar(team_names, best_player_score, best_player)
Season_bench_points.plot_offline()
# Season_bench_points.plot()

plot_data['filename'] = "remaining-drafted-players.html"
plot_data['title'] = "Number of Remaining Drafted Players"
Remaining_drafted_players = plot.Plot(plot_data)
Remaining_drafted_players.bar(player_changes.keys(), player_changes.values())
Remaining_drafted_players.plot_offline()
# Remaining_drafted_players.plot()
