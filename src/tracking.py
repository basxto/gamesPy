import logging
import psutil
import time
import datetime
import os

import games


class ProcessAttribution:
    def __init__(self, game, pid, started, absoluteProcess):
        self.game = game
        self.pid = pid
        self.started = started
        self.absoluteProcess = absoluteProcess


def track(trackedGames, config, storage, api):
    if not trackedGames:
        logging.info('Empty game list...')
        return
    logging.info('{} games are known'.format(len(trackedGames)))
    logging.info('Listening for newly started games...')
    try:
        while 1:
            # TODO: for now scanProcesses will only return array with at most one element
            found = scanProcesses(trackedGames, config, api)
            # trigger messages for start of tracking
            if len(found) > 0:
                game = found[0].game if len(found) == 1 else None
                api.onStart(game, found[0].started, found[0].pid, found[0].absoluteProcess)
                #TODO: start unfinished session object
            # wait for running process
            while len(found) != 0:
                # just take the first for now
                pa = found[0]
                try:
                    p = psutil.Process(pa.pid)
                    pinfo = p.as_dict(
                        attrs=['pid', 'name', 'create_time', 'cwd', 'cmdline', 'environ'])
                except psutil.NoSuchProcess:
                    # ambiguous matches must be decided later
                    # they will be put into a special tables
                    if len(found) > 1:
                        for pa in found:
                            tmpSession = games.Session(pa.game, datetime.datetime.fromtimestamp(
                                pa.started), datetime.datetime.now(), pa.absoluteProcess)
                            storage.addSession(tmpSession)
                        tmpSession = games.Session(None, datetime.datetime.fromtimestamp(
                            pa.started), datetime.datetime.now(), pa.absoluteProcess)
                        api.onQuit(tmpSession)
                    else:
                        tmpSession = games.Session(pa.game, datetime.datetime.fromtimestamp(
                            pa.started), datetime.datetime.now())
                        pa.game.addSession(tmpSession)
                        storage.addSession(tmpSession)
                        api.onQuit(tmpSession)
                    found = []
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
    # multiple matches are possible, we can’t exit early
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(
                attrs=['pid', 'name', 'exe', 'create_time', 'cwd', 'cmdline', 'environ'])
        except psutil.NoSuchProcess:
            pass
        else:
            execname = pinfo['exe'] or pinfo['name']
            # if the latter is an absolute path, the first will be ignored
            absoluteProcess = os.path.join(pinfo['cwd'] or '',execname)
            # eliminate symbolic links and collapse path
            absoluteProcess = os.path.realpath(absoluteProcess)
            for monitorid, game in trackedGames.items():
                # check if name is the same
                match = game.isProcess(pinfo, os.path.dirname(absoluteProcess))
                if match > 0:
                    pa = ProcessAttribution(
                        game, pinfo['pid'], pinfo['create_time'], absoluteProcess)
                    if match == 1:
                        found.append(pa)
                    else:
                        # with a perfect match we can stop immediately
                        # correct process (+ argument) + process path
                        return [pa]

    # check if we matched multiple processes
    if len(found) > 1:
        foundPid = found[0].pid
        for procattr in found:
            if procattr.pid != foundPid:
                logging.error('Matching multiple processes not supported!')
                for pa in found:
                    logging.debug('game {} ({}) matches for process {} (PID {}; CWD {})'.format(
                        pa.game.name, pa.game.process, pa.exe, pa.pid, pa.cwd))
                return []
    return found
