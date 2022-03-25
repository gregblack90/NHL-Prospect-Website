from flaskext.mysql import MySQL
import dbConfig
import pymysql
import json
import team_dictionary
import requests


def index_db_data(app):
    # connect to MySQL db, get all teams
    mysql = MySQL()
    app.config['MYSQL_DATABASE_USER'] = dbConfig.dbConfigInfo['user']
    app.config['MYSQL_DATABASE_PASSWORD'] = dbConfig.dbConfigInfo['password']
    app.config['MYSQL_DATABASE_DB'] = dbConfig.dbConfigInfo['database']
    app.config['MYSQL_DATABASE_HOST'] = dbConfig.dbConfigInfo['host']
    mysql.init_app(app)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams")
    entries = cursor.fetchall()

    # END OF DATABASE QUERIES, CLOSE CONNECTION
    conn.close()

    # RETURN DATA TO ROUTE
    return entries


def index_nhl_api_data():
    # GET STANDINGS FROM NHL API
    r = requests.get(url='https://statsapi.web.nhl.com/api/v1/standings')
    #   convert response data into json
    json_data_standings = r.json()
    #   get applicable data from json data
    league_data = json_data_standings['records']

    # RETURN DATA TO ROUTE
    return league_data
