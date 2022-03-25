from flask import render_template, flash, redirect, url_for, request
from app import app
# Import functions used to get data for index/home page
from data_func.index_page_func import index_db_data, index_nhl_api_data
# Import functions used to get data for team_page
from data_func.team_page_func import team_page_db_data, team_page_api_data
# Import functions used to get data for player_page
from data_func.player_page_func import player_page_db_data


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    # Get database data
    entries = index_db_data(app)

    # Get standings from NHL API
    league_data = index_nhl_api_data()

    # render home page template
    return render_template('index.html', title='Home',
                           entries=entries,
                           league_data=league_data)


@app.route('/team_page/<team>', methods=['GET', 'POST'])
def team_page(team):
    # Get database data
    prospects, no_prospects, team_conf_div = team_page_db_data(app, team)

    # Get NHL API Data
    team_data_stats, team_data_ranks = team_page_api_data(team)

    # render team page template
    return render_template('team_page.html', title=team,
                           team=team,
                           prospects=prospects,
                           no_prospects=no_prospects,
                           team_conf_div=team_conf_div,
                           team_data_stats=team_data_stats,
                           team_data_ranks=team_data_ranks)


@app.route('/player_page/<player>', methods=['GET', 'POST'])
def player_page(player):
    # Get database data
    game_log_data, no_game_log_data, opponent_all, player_info, age, curr_team_league, unique_season, data_dict, last_update, max_totals, season_totals = player_page_db_data(app, player)

    # render player page template
    return render_template('player_page.html',
                           title=player,
                           player=player,
                           game_log_data=game_log_data,
                           no_game_log_data=no_game_log_data,
                           opponent_all=opponent_all,
                           player_info=player_info,
                           age=age,
                           curr_team_league=curr_team_league,
                           unique_season=unique_season,
                           data_dict=data_dict,
                           last_update=last_update,
                           max_totals=max_totals,
                           season_totals=season_totals)
