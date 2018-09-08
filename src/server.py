#!/usr/bin/python3
from flask import Flask
from flask import jsonify
from flask import abort
import logging
import threading
import games
#import api
app = Flask(__name__)
appApi = None

@app.route('/')
def hello_world():
    return 'This is the RESTful API of games.py'

@app.route('/game/list')
def allGames():
    trackedGames = appApi.getGames()
    games = {}
    for monitorid, game in trackedGames.items():
        games[monitorid] = game.name
    return jsonify(games)

@app.route('/game/<id>')
def game(id):
    trackedGames = appApi.getGames()
    if id in trackedGames:
        game = trackedGames[id]
        return jsonify(id = id, name = game.name, process = game.process, argument = game.argument, processPath = game.processPath, playTime = appApi.deltaToDict(game.getPlaytime()))
    else:
        abort(404)

@app.route('/game/<id>/sessions')
def gameSessions(id):
    trackedGames = appApi.getGames()
    if id in trackedGames:
        game = trackedGames[id]
        sessions = []
        for session in game.sessions:
            sessions.append({"start":session.start.timestamp(),"end":session.end.timestamp()})
        return jsonify(sessions)
    else:
        abort(404)
def flaskThread(host,port,api):
    global appApi
    appApi = api
    app.run(host, port)