import logging
import datetime
# regex
import re


class Session:
    def __init__(self, game, start, end, absoluteProcess=''):
        self.game = game
        self.start = start
        self.end = end
        # this is only for ambiguous sessions
        self.absoluteProcess = absoluteProcess
    # returns a time delta

    def getDuration(self):
        return self.end - self.start


class SaveGame:
    def __init(self):
        self.path = ''
        self.include = ''
        self.exclude = ''


class Game:
    def __init__(self, name, process, argument='', processPath='', monitorid='unknown', isRegex=False):
        self.name = name
        self.process = process
        # process is regex format
        self.isRegex = isRegex
        self.argument = argument
        self.processPath = processPath
        self.monitorid = monitorid
        self.sessions = []
        self.saveGame = SaveGame()

    def processCompare(self, process):
        if self.isRegex:
            regex = re.compile(self.process + '$')
            return (process and regex.search(process))
        else:
            return (process and process.endswith(self.process))

    # 0: no; 1: yes; 2: perfect fit
    def isProcess(self, pinfo, processPath):
        # check process name
        if (not self.processCompare(pinfo['name'])
                and not self.processCompare(pinfo['exe'])):
            return 0
        # "only check if argument exists
        if self.argument != '':
            # compare argument with every cmdline argument
            argument = re.compile(self.argument)
            if [arg for arg in pinfo['cmdline'] if argument.search(arg)]:
                pass
            else:
                return 0

        # only check if process path exists
        # otherwise fall back to multi 
        if (self.processPath != '' and self.processPath == processPath):
            return 2
        return 1

    def addSession(self, session):
        self.sessions.append(session)

    def getSessions(self, ambiguous = False):
        sessions = []
        #TODO: filter
        for session in self.sessions:
            # xor inverts the expression when ambiguous = True
            if (session.absoluteProcess == '') ^ ambiguous:
                session.append(session)
        return sessions

    # Returns time delta
    def getPlaytime(self):
        timeAccu = datetime.timedelta()
        for session in self.getSessions():
            timeAccu += session.getDuration()
        return timeAccu
