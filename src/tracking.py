import logging
import psutil
import time
import datetime

import games

def track(trackedGames, config, storage, api):
    if not trackedGames:
        logging.info('Empty game list...')
        return
    logging.info('{} games are known'.format(len(trackedGames)))
    logging.info('Listening for newly started games...')
    try:
        found = {'pid': -1, 'game': None, 'started': 0}
        while 1:
            scanProcesses(found, trackedGames, config, api)
            # wait for running process
            while found['pid'] != -1:
                try:
                    p = psutil.Process(found['pid'])
                    pinfo = p.as_dict(attrs=['pid', 'name', 'create_time', 'cwd', 'cmdline', 'environ'])
                except psutil.NoSuchProcess:
                    tmpSession = games.Session(found['game'], datetime.datetime.fromtimestamp(pinfo['create_time']), datetime.datetime.now())
                    found['game'].addSession(tmpSession)
                    storage.addSession(tmpSession)
                    found['pid'] = -1
                    api.onQuit(tmpSession)
                else:
                    try:
                        # wait for process to exit or 5 seconds
                        p.wait(5)
                    except psutil.TimeoutExpired:
                        pass
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info('Stopped listening for newly started games...\n')

def scanProcesses(found, trackedGames, config, api):
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
                    found['started'] = pinfo['create_time']
                    api.onStart(found['game'], found['started'], found['pid'])
                    break
                if found['pid'] != -1:
                    break
            if found['pid'] != -1:
                break