#!/usr/bin/python3
from flask import Flask
from flask import jsonify
from flask import abort
from flask import request
import logging
import threading
import games
#import api
app = Flask(__name__)
appApi = None

@app.route('/')
def hello_world():
    return 'This is the RESTful API of games.py'

@app.route('/session/list', methods=['GET'])
def listSessions():
    sessionObjects = appApi.getSessions()
    sessions = []
    for session in sessionObjects:
        sessions.append({"start": session.start.timestamp(), "end": session.end.timestamp(), "id": session.game.monitorid})
    return jsonify(sessions)

#sessions the tracker couldn’t clearly assign to a game
@app.route('/session/unassigned', methods=['GET'])
def unassignedSessions():
    return 'Coming soon...'

@app.route('/game/list', methods=['GET'])
def listGames():
    trackedGames = appApi.getGames()
    games = {}
    for monitorid, game in trackedGames.items():
        games[monitorid] = game.name
    return jsonify(games)

@app.route('/game/current', methods=['GET'])
def currentGame():
    return 'Coming soon...'

@app.route('/game/<id>', methods=['GET', 'POST'])
def game(id):
    if request.method == 'POST':
        appApi.setGame(id, request.get_json(True))
    #always show
    trackedGames = appApi.getGames()
    if id in trackedGames:
        game = trackedGames[id]
        return jsonify(id = id, name = game.name, process = game.process, argument = game.argument, processPath = game.processPath, playTime = appApi.deltaToDict(game.getPlaytime()))
    else:
        abort(404)

@app.route('/game/<id>/sessions', methods=['GET'])
def gameSessions(id):
    trackedGames = appApi.getGames()
    if id in trackedGames:
        game = trackedGames[id]
        sessions = []
        for session in game.sessions:
            sessions.append({"start": session.start.timestamp(), "end": session.end.timestamp()})
        return jsonify(sessions)
    else:
        abort(404)
def flaskThread(host,port,api):
    global appApi
    appApi = api
    app.run(host, port)