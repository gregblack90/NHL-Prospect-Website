from flaskext.mysql import MySQL
import dbConfig
import pymysql
import json
import team_dictionary
import requests
import time
from datetime import date, datetime
from collections import OrderedDict


def team_page_db_data(app, team):
    # connect to MySQL db, get prospects for team that was clicked (see index.html)
    mysql = MySQL()
    app.config['MYSQL_DATABASE_USER'] = dbConfig.dbConfigInfo['user']
    app.config['MYSQL_DATABASE_PASSWORD'] = dbConfig.dbConfigInfo['password']
    app.config['MYSQL_DATABASE_DB'] = dbConfig.dbConfigInfo['database']
    app.config['MYSQL_DATABASE_HOST'] = dbConfig.dbConfigInfo['host']
    mysql.init_app(app)
    conn = mysql.connect()
    cursor = conn.cursor()

    # GET SELECTED TEAM's PROSPECTS
    sql = "SELECT * FROM prospects WHERE team =%s"
    val = team
    cursor.execute(sql, val)
    prospects_tup = cursor.fetchall()
    # create empty lists for prospects or no prospect bit
    prospects = []
    no_prospects = []
    # if prospects exist
    if len(prospects_tup) > 0:
        # FOR SELECTED TEAM GET PROSPECT INFO
        # data retrieved as a tuple, need to convert to list in order to append age after calculation
        prospects_list = [list(row) for row in prospects_tup]
        for prospect in prospects_list:
            # calculate age
            dob = prospect[5]
            b_mon = int(dob[0:2])
            b_day = int(dob[3:5])
            b_year = int(dob[6:10])
            today = date.today()
            age = today.year - b_year - ((today.month, today.day) < (b_mon, b_day))
            # append age to player data
            prospect.append(age)
            # append player data to whole list of lists
            prospects.append(prospect)
    # if no prospects exist
    else:
        no_prospects.append('True')

    # GET SELECTED TEAM'S CONFERENCE AND DIVISION
    sql_conf_div = 'SELECT * FROM teams WHERE Team=%s'
    val_conf_div = team
    cursor.execute(sql_conf_div, val_conf_div)
    team_conf_div_val = cursor.fetchall()
    team_conf_div = team_conf_div_val[0]

    # END OF DATABASE QUERIES - close db connection
    conn.close()

    # RETURN DATA TO ROUTE
    return prospects, no_prospects, team_conf_div


def team_page_api_data(team):
    # SELECTED TEAM'S CURRENT STANDINGS
    #   get team ID needed for NHL API
    team_id = str(team_dictionary.team_dict[team])
    #   query NHL API for records of selected team
    r = requests.get(url='https://statsapi.web.nhl.com/api/v1/teams/' + team_id + '/stats')
    #   convert response data into json
    json_data_team = r.json()
    #   get applicable data from json data
    team_data_stats = json_data_team['stats'][0]['splits'][0]['stat']
    team_data_ranks = json_data_team['stats'][1]['splits'][0]['stat']

    # RETURN DATA TO ROUTE
    return team_data_stats, team_data_ranks
