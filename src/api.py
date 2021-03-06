import logging
import subprocess
import datetime


class Api:
    def __init__(self, config):
        self.config = config

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
        seconds = session.getDuration().seconds
        minutes = seconds/60
        hours = minutes/60
        logging.info('This session of {} took {}h {}min {}sec'.format(
            name, round(hours), round(minutes % 60), seconds % 60))
        if session.game:
            totSeconds = session.game.getPlaytime().seconds
            totMinutes = totSeconds/60
            totHours = totMinutes/60
            logging.info('You played {} {}h {}min {}sec in total'.format(
                session.game.name, round(totHours % 24), round(totMinutes % 60), totSeconds % 60))
            subprocess.Popen(self.config['RUN']['onquit'].format(name=session.game.name, id=session.game.monitorid, savePath='', saveInclude='', saveExclude='', h=round(hours%24),m=round(minutes%60),s=seconds%60, start=session.start.timestamp()), shell=True)
