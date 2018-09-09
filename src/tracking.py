import logging
import psutil
import time
import datetime

import games

class ProcessAttribution:
    def __init__(self, game, pid, exe, cwd, started):
        self.game = game
        self.pid = pid
        self.exe = exe
        self.cwd = cwd
        self.started = started

def track(trackedGames, config, storage, api):
    if not trackedGames:
        logging.info('Empty game list...')
        return
    logging.info('{} games are known'.format(len(trackedGames)))
    logging.info('Listening for newly started games...')
    try:
        while 1:
            #TODO: for now scanProcesses will only return array with at most one element
            found = scanProcesses(trackedGames, config, api)
            # wait for running process
            while len(found) != 0:
                #just take the first for now
                pa = found[0]
                try:
                    p = psutil.Process(pa.pid)
                    pinfo = p.as_dict(attrs=['pid', 'name', 'create_time', 'cwd', 'cmdline', 'environ'])
                except psutil.NoSuchProcess:
                    tmpSession = games.Session(pa.game, datetime.datetime.fromtimestamp(pa.started), datetime.datetime.now())
                    pa.game.addSession(tmpSession)
                    storage.addSession(tmpSession)
                    found = []
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

def scanProcesses(trackedGames, config, api):
    found = []
    #multiple matches are possible, we can’t exit early
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
                    pa = ProcessAttribution(game, pinfo['pid'], pinfo['exe'], pinfo['cwd'], pinfo['create_time'])
                    found.append(pa)

    #check if we matched mutliple games
    if len(found) > 1:
        foundPid = found[0].pid
        for procattr in found:
            if procattr.pid != foundPid:
                logging.error('Matching multiple processes not supported!')
                for pa in found:
                    logging.debug('game {} ({}) matches for process {} (PID {}; CWD {})'.format(pa.game.name, pa.game.process, pa.exe, pa.pid, pa.cwd))
                return []
    if len(found) > 0:
        api.onStart(found[0].game, found[0].started, found[0].pid)
    return found