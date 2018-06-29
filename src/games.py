import logging
import datetime
# regex
import re

class Session:
    def __init__(self, game, start, end):
        self.game = game
        self.start = start
        self.end = end
    # returns a time delta
    def getDuration(self):
        return self.end - self.start

class Game:
    def __init__(self, name, process, argument='', processPath='', monitorid='unknown'):
        self.name = name
        self.process = process
        self.argument = argument
        self.processPath = processPath
        self.monitorid = monitorid
        self.sessions = []
        self.lookalikes = []
    def isProcess(self, pinfo):
        # check process name
        #TODO: work with  explicit binary extensions
        binaryExtension = '(\\.(exe|run|elf|bin))?(\\.(x86(_64)?|(amd|x)64))?'
        name = re.compile(self.process + binaryExtension + '$')
        if( not (pinfo['name'] and name.search(pinfo['name']) )
        and not (pinfo['exe' ] and name.search(pinfo['exe' ]) )):
            return False
        #TODO: thanks to regex we can't rely on .lookalikes any longer
        # a daemon can't ask the user which game this is
        # a client would have to clarify this
        if self.lookalikes and (self.processPath != pinfo['cwd']):
            logging.warning('Process name is ambiguous.')
            logging.warning('There is no process path stored to distinguish these games.')
            return False
        # No argument is always contained
        if not self.argument:#!!!
            return True
        # compare argument with every cmdline argument
        argument = re.compile(self.argument)
        if [arg for arg in pinfo['cmdline'] if argument.search(arg)]:
            return True
        else:
            return False
    def addSession(self, session):
        self.sessions.append(session)
    # Returns time delta
    def getPlaytime(self):
        timeAccu = datetime.timedelta()
        for session in self.sessions:
            timeAccu += session.getDuration()
        return timeAccu