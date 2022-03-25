from flaskext.mysql import MySQL
import dbConfig
import pymysql
import json
import team_dictionary
import requests
import time
from datetime import date, datetime
from collections import OrderedDict


def player_page_db_data(app, player):
    # connect to MySQL db, get game log data for player that was clicked
    mysql = MySQL()
    app.config['MYSQL_DATABASE_USER'] = dbConfig.dbConfigInfo['user']
    app.config['MYSQL_DATABASE_PASSWORD'] = dbConfig.dbConfigInfo['password']
    app.config['MYSQL_DATABASE_DB'] = dbConfig.dbConfigInfo['database']
    app.config['MYSQL_DATABASE_HOST'] = dbConfig.dbConfigInfo['host']
    mysql.init_app(app)
    conn = mysql.connect()
    cursor = conn.cursor()

    # GET GAME LOG DATA
    #   format player name for sql query
    #       get rid of spaces between names
    sql_player_0 = player.replace(" ", "")
    #       get rid of any hyphens in name
    sql_player = sql_player_0.replace("-", "")
    #   assemble sql query
    #       can only select common rows between all leagues:
    #           --> Date, Season, Team, League, Opponent, Goals, Assists, Total, PIM, SOG, PlusMinus
    sql = "SELECT Date, Season, Team, League, Opponent, Goals, Assists, Total, PIM, SOG, PlusMinus " \
          "FROM " + sql_player + ""
    #   create empty lists for game log data or in case player doesn't exists in database yet
    game_log_data = []
    no_game_log_data = []
    try:
        #   get game log data
        cursor.execute(sql)
        game_log_data = cursor.fetchall()

        # GET DATE OF LAST UPDATE
        #   assemble sql query
        sql_update_time = "SELECT Date, Time FROM update_time WHERE Player=%s"
        val_update_time = sql_player
        #   get update time
        cursor.execute(sql_update_time, val_update_time)
        update_time_query = cursor.fetchall()
        #   create variable for update time
        if len(update_time_query) > 0:
            update_time_data = update_time_query[0]
            update_date = update_time_data[0].strftime("%m/%d/%Y")
            update_time = update_time_data[1]
            last_update = update_date + ' @ ' + update_time[:5]
        else:
            last_update = 'N/A'

        # GET CURRENT TEAM AND LEAGUE
        sql_current_team = "SELECT * from current_team WHERE Player=%s"
        val_current_team = sql_player
        cursor.execute(sql_current_team, val_current_team)
        current_team_tup = cursor.fetchall()
        curr_team_league = []
        if len(current_team_tup) > 0:
            # if an entry for player exists in current_team table
            current_team = current_team_tup[0][1]
            current_league = current_team_tup[0][2]
            curr_team_league.extend([current_team, current_league])
        else:
            # if an entry for player does not exist in current_team table
            curr_team_league.extend(['N/A', 'N/A'])

        # GET PLAYER INFORMATION
        #   sql statements for player information
        sql_player_data = "SELECT * from prospects WHERE Name=%s"
        val_player_data = player
        #   get player information
        cursor.execute(sql_player_data, val_player_data)
        player_info_tup = cursor.fetchall()
        #   set player information
        player_info = player_info_tup[0]
        #   calculate age
        dob = player_info[5]
        b_mon = int(dob[0:2])
        b_day = int(dob[3:5])
        b_year = int(dob[6:10])
        today = date.today()
        age = today.year - b_year - ((today.month, today.day) < (b_mon, b_day))

        # GET UNIQUE SEASONS
        #   create empty list for values
        unique_season = []
        #   sql statements for db query
        sql_unique_season = "SELECT DISTINCT Season FROM " + sql_player + " WHERE SOG !=%s"
        val_unique_season = "Exhibition"
        #   query database
        cursor.execute(sql_unique_season, val_unique_season)
        unique_season_tup = cursor.fetchall()
        for season in unique_season_tup:
            unique_season.append(season[0])

        # GET CUMULATIVE OF GOALS, ASSISTS, POINTS BY SEASON
        #   Create empty dictionary
        data_dict = {}
        #   Create empty dictionary for max of goals, assists, points, games played
        max_totals = {}

        for season in unique_season:
            #   Get dates for unique season
            sql_cumul_date = "SELECT Date FROM " + sql_player + " WHERE (Season=%s AND SOG !=%s)"
            val_cumul = season, "Exhibition"
            cursor.execute(sql_cumul_date, val_cumul)
            date_data = cursor.fetchall()
            #   Get goals for unique season
            sql_cumul_goals = "SELECT Goals FROM " + sql_player + " WHERE (Season=%s AND SOG !=%s)"
            cursor.execute(sql_cumul_goals, val_cumul)
            goals_data = cursor.fetchall()
            #   Get assists for unique season
            sql_cumul_assists = "SELECT Assists FROM " + sql_player + " WHERE (Season=%s AND SOG !=%s)"
            cursor.execute(sql_cumul_assists, val_cumul)
            assists_data = cursor.fetchall()
            #   Get points for unique season
            sql_cumul_points = "SELECT Total FROM " + sql_player + " WHERE (Season=%s AND SOG !=%s)"
            cursor.execute(sql_cumul_points, val_cumul)
            points_data = cursor.fetchall()
            #   Convert data into lists
            dates = []
            for date_i in date_data:
                dates.append(date_i[0].strftime("%m/%d/%Y"))
            goals = []
            for goal_i in goals_data:
                goals.append(goal_i[0])
            assists = []
            for assists_i in assists_data:
                assists.append(assists_i[0])
            points = []
            for points_i in points_data:
                points.append(points_i[0])
            #   Assemble cumulative lists
            #   Goals
            cumul_goals = []
            total_goals = 0
            for goal_j in goals:
                if goal_j == 'DNP':
                    total_goals = total_goals + 0
                else:
                    total_goals = total_goals + int(goal_j)
                cumul_goals.append(str(total_goals))
            #   Assists
            cumul_assists = []
            total_assists = 0
            for assists_j in assists:
                if assists_j == 'DNP':
                    total_assists = total_assists + 0
                else:
                    total_assists = total_assists + int(assists_j)
                cumul_assists.append(str(total_assists))
            #   Points
            cumul_points = []
            total_points = 0
            for points_j in points:
                if points_j == 'DNP':
                    total_points = total_points + 0
                else:
                    total_points = total_points + int(points_j)
                cumul_points.append(str(total_points))
            #   Assemble max totals and GP lists
            #   Games Played
            #       to get accurate number, need to remove "DNP" dates
            games_played_data = []
            for games in goals_data:
                if games[0] == 'DNP':
                    continue
                else:
                    games_played_data.append(games[0])
            #       number used for games played (excludes 'DNP's)
            games_played_num = len(games_played_data)
            #       number used to access cumulative lists (includes 'DNP's)
            games_played = len(dates)
            #       change value to string in order to add to dictionary
            num_games_pass = str(games_played_num)
            #   Max Goals
            max_goals = str(cumul_goals[games_played - 1])
            #   Max Assists
            max_assists = str(cumul_assists[games_played - 1])
            #   Max Points
            max_points = str(cumul_points[games_played - 1])
            #   Get number of games played and create list
            games_played_sch = len(cumul_goals)
            games_played_num_pass = [i for i in range(1, games_played_sch + 1)]
            #   Append new data to dictionary
            data_dict[season] = {'Goals': cumul_goals, 'Assists': cumul_assists, 'Points': cumul_points, 'Dates': dates,
                                 'GP': games_played_num_pass}
            max_totals[season] = {'Goals': max_goals, 'Assists': max_assists, 'Points': max_points,
                                  'GP': num_games_pass}

        # GET SEASON TOTALS BY TEAM
        # needed to account for when players are traded mid season.
        # 1. get unique seasons
        # 2. for each unique season, get teams played for that season
        # 3. for each team played for that season, get total of goals, assists, points and games played
        # 4. add data from step 3 to dictionary (team = key)
        # 5. once all teams have been looped through for unique season, add data from step 4 to dictionary (season = key)
        #
        #   create empty list for values
        season_totals = {}
        #   sql statements for db query
        sql_unique_season = "SELECT DISTINCT Season FROM " + sql_player + " WHERE SOG !=%s"
        val_unique_season = "Exhibition"
        #   query database
        cursor.execute(sql_unique_season, val_unique_season)
        unique_season_tup = cursor.fetchall()
        #   for each unique season...
        for season in unique_season_tup:
            #   set season
            league_year = season[0]
            #   get unique teams for that season (in case player got traded mid season)
            sql_unique_season_team = "SELECT DISTINCT Team From " + sql_player + " WHERE (SOG!=%s AND Season =%s )"
            val_unique_season_team = "Exhibition", season
            cursor.execute(sql_unique_season_team, val_unique_season_team)
            unique_season_team_tup = cursor.fetchall()
            #   create empty dict for values
            season_team_totals = {}
            #   for each team within the season...
            for team in unique_season_team_tup:
                #       get game log data for specified team and season
                sql_unique_season_team_stats = "SELECT * From " + sql_player + \
                                               " WHERE (SOG!=%s AND Team =%s AND Season =%s )"
                val_unique_season_team_stats = "Exhibition", team, season
                cursor.execute(sql_unique_season_team_stats, val_unique_season_team_stats)
                unique_season_team_stats_tup = cursor.fetchall()
                #       set team name
                team_key = team[0]
                #       set league of team
                team_league_key = unique_season_team_stats_tup[0][3]
                #       create empty lists
                goals_team = []
                assists_team = []
                points_team = []
                #       for each game with specified team and season...
                for game in unique_season_team_stats_tup:
                    #           create list of goals, assists and point values
                    goals_team.append(game[6])
                    assists_team.append(game[7])
                    points_team.append(game[8])
                #       set counters
                goals_team_num = 0
                assists_team_num = 0
                points_team_num = 0
                #       for goals, assists and points...loop over list and get cumulative total of values
                for goal_k in goals_team:
                    goals_team_num = goals_team_num + int(goal_k)
                for assist_k in assists_team:
                    assists_team_num = assists_team_num + int(assist_k)
                for point_k in points_team:
                    points_team_num = points_team_num + int(point_k)
                #       get games played
                gp_team_num = len(goals_team)
                #       add stats for specified year for specified team
                season_team_totals[team_key] = {'League': team_league_key, 'GP': gp_team_num,
                                                'G': goals_team_num, 'A': assists_team_num, 'P': points_team_num}
            #   after looping over seasons for a specific team, add that data to dictionary
            season_totals[league_year] = season_team_totals

    #   following error is generated if player game log table does not exist:
    #   --> pymysql.err.ProgrammingError: (1146, "Table 'NHL.PlayerName' doesn't exist")
    except pymysql.err.ProgrammingError:
        #   set flag for no data to True,
        no_game_log_data.append('True')
        player_info = []
        age = ''
        curr_team_league = ['', '']
        unique_season = []
        data_dict = []
        last_update = ''
        max_totals = []
        season_totals = []
    # end of database queries - close db connection
    conn.close()

    # need to format Opponent and get league and team from each season
    #   add opponent to list
    opponent_all = []
    for game in game_log_data:
        opp = game[4]
        #   get rid of "at "
        if opp[:3] == "at " or "vs ":
            opp = opp.replace("at ", "")
            opp = opp.replace("vs ", "")
        #   capitalize first letter of word in string
        opp_new = opp.title()
        opponent_all.append(opp_new)

    # RETURN DATA TO ROUTE
    return game_log_data, no_game_log_data, opponent_all, player_info, age, curr_team_league, unique_season, data_dict, last_update, max_totals, season_totals
