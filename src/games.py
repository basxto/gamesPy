import logging
import datetime
# regex
import re


class Session:
    def __init__(self, game, start, end, ambiguous=False, matches=[]):
        self.game = game
        self.start = start
        self.end = end
        self.ambiguous = ambiguous
        self.matches = matches
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

    def isProcess(self, pinfo):
        # check process name
        # TODO: work with  explicit binary extensions
        if (not self.processCompare(pinfo['name'])
                and not self.processCompare(pinfo['exe'])):
            return False
        # "No argument" is always contained
        if not self.argument:  # !!!
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
