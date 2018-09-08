import logging
import subprocess
import datetime
import storage
import math

class Api:
    def __init__(self, config):
        self.config = config

    #thread safe
    def getGames(self):
        store = storage.Database(self.config['DATABASE']['path'], False)
        trackedGames = {}
        store.getGames(trackedGames)
        return trackedGames

    def getSessions(self):
        trackedGames = self.getGames()
        sessions = []
        for id, game in trackedGames.items():
            logging.debug(game)
            for session in game.sessions:
                sessions.append(session)
        return sessions


    def onStart(self, game, started, pid):
        logging.info('{name} has PID {pid} and was started {start}'.format(name=game.name,pid=pid,start=datetime.datetime.fromtimestamp(started).strftime("%Y-%m-%d %H:%M:%S")))
        subprocess.Popen(self.config['RUN']['onstart'].format(name=game.name, id=game.monitorid, start=started), shell=True)

    def deltaToDict(self, delta):
        seconds = (delta.seconds)%60
        minutes = math.floor( (seconds/60)%60 )
        hours = math.floor( minutes/60 )
        return {'seconds': seconds, 'minutes': minutes, 'hours': hours}
        
    
    def onQuit(self, session):
        sg=session.game.saveGame
        duration = self.deltaToDict(session.getDuration())
        played = self.deltaToDict(session.game.getPlaytime())
        logging.info('This session of {} took {}h {}min {}sec'.format(session.game.name, duration.hours,duration.minutes,duration.seconds))
        logging.info('You played {} {}h {}min {}sec in total'.format(session.game.name, played.hours,played.minutes,played.seconds))
        subprocess.Popen(self.config['RUN']['onquit'].format(name=session.game.name, id=session.game.monitorid, savePath=sg.path, saveInclude=sg.include, saveExclude=sg.exclude, h=duration.hours,m=duration.minutes,s=duration.seconds, start=session.start.timestamp()), shell=True)