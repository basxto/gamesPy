#!/usr/bin/python3
from flask import Flask
from flask import jsonify
import logging
import threading
#import api
app = Flask(__name__)
appApi = None

@app.route('/')
def hello_world():
    return 'Hello, World!'
@app.route('/getGames')
def start():
    ##Api.onStart();
    trackedGames = appApi.getGames()
    games = {}
    for monitorid, game in trackedGames.items():
        games[monitorid] = game.name
    return jsonify(games)
def flaskThread(host,port,api):
    global appApi
    appApi = api
    app.run(host, port)