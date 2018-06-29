import logging
import psutil
import subprocess
import time
import datetime

import games

def track(trackedGames, config, storage, dryRun):
    if not trackedGames:
        logging.info('Empty game list...')
        return
    logging.info('{} games are known'.format(len(trackedGames)))
    logging.info('Listening for newly started games...')
    try:
        found = {'pid': -1, 'game': None, 'started': 0}
        while 1:
            for proc in psutil.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'exe', 'create_time', 'cwd', 'cmdline', 'environ'])
                except psutil.NoSuchProcess:
                    pass
                else:
                    for monitorid, game in trackedGames.items():
                        # check if name is the same
                        # if set also check argument
                        if game.isProcess(pinfo):
                            found['pid'] = pinfo['pid']
                            found['game'] = game
                            found['startedu'] = pinfo['create_time']
                            logging.info('{name} has PID {pid} and was started {start}'.format(name=game.name,pid=pinfo['pid'],start=datetime.datetime.fromtimestamp(pinfo['create_time']).strftime("%Y-%m-%d %H:%M:%S")))
                            # run custom program on start
                            subprocess.Popen(config['RUN']['onstart'].format(name=found['game'].name, id=found['game'].monitorid, start=pinfo['create_time']), shell=True)
                            break
                        if found['pid'] != -1:
                            break
                    if found['pid'] != -1:
                        break
            # wait for running process
            while found['pid'] != -1:
                try:
                    p = psutil.Process(found['pid'])
                    pinfo = p.as_dict(attrs=['pid', 'name', 'create_time', 'cwd', 'cmdline', 'environ'])
                except psutil.NoSuchProcess:
                    tmpSession = games.Session(found['game'], datetime.datetime.fromtimestamp(pinfo['create_time']), datetime.datetime.now())
                    seconds = tmpSession.getDuration().seconds
                    minutes = seconds/60
                    hours = minutes/60
                    logging.info('This session of {} took {}h {}min {}sec'.format(found['game'].name, round(hours%24),round(minutes%60),seconds%60))
                    #hour in float
                    found['game'].addSession(tmpSession)
                    if not dryRun:
                        storage.addSession(tmpSession)
                    logging.info('You played {} {}h {}min {}sec in total'.format(found['game'].name, round((found['game'].getPlaytime().seconds/3600)%24),round((found['game'].getPlaytime().seconds/60)%60),found['game'].getPlaytime().seconds%60))
                    found['pid'] = -1
                    # run custom program on end
                    subprocess.Popen(config['RUN']['onquit'].format(name=found['game'].name, h=round(hours%24),m=round(minutes%60),s=seconds%60, id=found['game'].monitorid, start=tmpSession.start.timestamp()), shell=True)
                else:
                    try:
                        # wait for process to exit or 5 seconds
                        p.wait(5)
                    except psutil.TimeoutExpired:
                        pass
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info('Stopped listening for newly started games...\n')