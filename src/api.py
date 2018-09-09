import logging
import subprocess
import datetime
import storage
import math


class Api:
    def __init__(self, config):
        self.config = config

    # thread safe
    def getGames(self):
        store = storage.Database(self.config['DATABASE']['path'], False)
        trackedGames = {}
        store.getGames(trackedGames)
        return trackedGames

    # thread safe
    # game is just a dict
    def setGame(self, id, newGame):
        store = storage.Database(self.config['DATABASE']['path'], False)
        trackedGames = {}
        store.getGames(trackedGames)
        game = trackedGames[id]
        for attr, val in newGame.items():
            if attr == 'name':
                game.name = val
            elif attr == 'process':
                game.process = val
            elif attr == 'argument':
                game.argument = val
        store.addGame(game)
        return trackedGames

    def getSessions(self):
        trackedGames = self.getGames()
        sessions = []
        for id, game in trackedGames.items():
            logging.debug(game)
            for session in game.getSessions():
                sessions.append(session)
        return sessions

    def deltaToDict(self, delta):
        seconds = (delta.seconds) % 60
        minutes = math.floor((seconds/60) % 60)
        hours = math.floor(minutes/60)
        return {'seconds': seconds, 'minutes': minutes, 'hours': hours}

    def onStart(self, game, started, pid, absoluteProcess):
        name = absoluteProcess
        if game:
            name = game.name
            subprocess.Popen(self.config['RUN']['onstart'].format(
                name=game.name, id=game.monitorid, start=started), shell=True)
        logging.info('{name} has PID {pid} and was started {start}'.format(
            name=name, pid=pid, start=datetime.datetime.fromtimestamp(started).strftime("%Y-%m-%d %H:%M:%S")))

    def onQuit(self, session):
        name = session.absoluteProcess
        if session.game:
            name = session.game.name
        duration = self.deltaToDict(session.getDuration())
        logging.info('This session of {} took {}h {}min {}sec'.format(
            name, duration['hours'], duration['minutes'], duration['seconds']))
        if session.game:
            played = self.deltaToDict(session.game.getPlaytime())
            logging.info('You played {} {}h {}min {}sec in total'.format(
                session.game.name, played['hours'], played['minutes'], played['seconds']))
            subprocess.Popen(self.config['RUN']['onquit'].format(name=session.game.name, id=session.game.monitorid, savePath='', saveInclude='',
                                                                 saveExclude='', h=duration['hours'], m=duration['minutes'], s=duration['seconds'], start=session.start.timestamp()), shell=True)
