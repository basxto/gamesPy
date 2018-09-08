import logging
import sqlite3
import datetime
import sqlite3
import socket # for hostname
# xml import
import urllib.request
import uuid
import xml.etree.ElementTree as ET

import games

class Database:
    def __init__(self, path, dryRun=False):
        self.dryRun=dryRun
        self.appVer = 112
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.createDatabase()

    def createDatabase(self):
        # compatible to GBM v1.04
        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS `sessions` (
                        `MonitorID` TEXT NOT NULL,
                        `Start` INTEGER NOT NULL,
                        `End` INTEGER NOT NULL,
                        `ComputerName` TEXT NOT NULL,
                        PRIMARY KEY(MonitorID, Start)
                    )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS `monitorlist` (
                        `MonitorID`     TEXT    NOT NULL UNIQUE,
                        `Name`          TEXT    NOT NULL,
                        `Process`       TEXT    NOT NULL,
                        `IsRegex`       BOOLEAN NOT NULL,
                        `Path`          TEXT,
                        `AbsolutePath`  BOOLEAN NOT NULL,
                        `FolderSave`    BOOLEAN NOT NULL,
                        `FileType`      TEXT,
                        `ExcludeList`   TEXT    NOT NULL,
                        `ProcessPath`   TEXT,
                        `Version`       TEXT,
                        `Enabled`       BOOLEAN NOT NULL,
                        `MonitorOnly`   BOOLEAN NOT NULL,
                        `BackupLimit`   INTEGER NOT NULL,
                        `CleanFolder`   BOOLEAN NOT NULL,
                        `Parameter`     TEXT,
                        `Comments`      TEXT,
                        PRIMARY KEY(`Name`, `Process`)
                    );''')
        cur.close()

    def getGames(self, trackedGames):
        #TODO this does not work any longer, we use regex now
        ambiguous = {}
        cur = self.conn.cursor()
        cur.execute('SELECT `Process`, `Parameter`, COUNT(*) AS Occurrences FROM `monitorlist` GROUP BY `Process`, `Parameter` HAVING ( COUNT(*) > 1)')
        for row in cur:
            ambiguous[row["Process"]] = {'parameter':row["Parameter"], 'games':[]}
        cur.execute('SELECT `MonitorID`, `Name`, `Process`, `Parameter`, `ProcessPath` FROM `monitorlist`')
        for row in cur:
            trackedGames[row["MonitorID"]] = games.Game(row["Name"], row["Process"], row["Parameter"], row["ProcessPath"], row["MonitorID"])
            # mark games with ambiguous process names
            if (row["Process"] in ambiguous) and (ambiguous[row["Process"]]['parameter'] == row["Parameter"]):
                trackedGames[row["MonitorID"]].lookalikes = ambiguous[row["Process"]]['games']
                ambiguous[row["Process"]]['games'].append(trackedGames[row["MonitorID"]])
        cur.execute('SELECT `MonitorID`, `Start`, `End` FROM `sessions`')
        for row in cur:
            trackedGames[row["MonitorID"]].addSession(games.Session(trackedGames[row["MonitorID"]], datetime.datetime.fromtimestamp(row["Start"]), datetime.datetime.fromtimestamp(row["End"])))
        cur.close()

    def addSession(self, session):
        if self.dryRun:
            logging.debug('Skipped addSession')
            return
        # use connection as a context manager
        try:
            with self.conn:
                self.conn.execute('INSERT INTO `sessions` (`MonitorID`, `Start`, `End`, `ComputerName`) VALUES (?, ?, ?, ?)',
                (session.game.monitorid, session.start.timestamp(), session.end.timestamp(), socket.gethostname()))
        except sqlite3.IntegrityError:
            logging.error("Couldn't add session to database")
    #def changeGame(self, game): TODO

    def addGame(self, game):
        self.addPlainGame(game.name, game.process, False, game.argument, game.monitorid, '', '', '', '', True, '')

    def addPlainGame(self, name, process, isRegex, parameter, monitorId, absolutePath, folderSave, includeList, excludeList, monitorOnly, comments):
        if self.dryRun:
            logging.debug('Skipped addPlainGame')
            return
        try:
            with self.conn:
                # much ballast from gbm
                self.conn.execute('INSERT or REPLACE INTO `monitorlist` (`Name`, `Process`, `IsRegex`, `Parameter`, `MonitorID`, `AbsolutePath`, `FolderSave`, `ExcludeList`, `MonitorOnly`, `Comments`, `Enabled`, `TimeStamp`, `BackupLimit`, `CleanFolder`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (name, process, isRegex, parameter, monitorId, absolutePath, folderSave, excludeList, monitorOnly, comments, True, False, 2, False))
        except sqlite3.IntegrityError:
            logging.error("Couldn't add game {} to database".format(name))

    # parse xml game list
    # date = 0 updates always
    def importGames(self, url, date='0'):
        try:
            with urllib.request.urlopen(url) as f:
                gameList = ET.fromstring(f.read().decode('utf-8'))
                if not gameList.attrib['AppVer'] or int(gameList.attrib['AppVer']) > self.appVer:
                    logging.warning('XML format of game list is too new')
                else:
                    logging.info('URL: {}\n- Format version: {}\n- Contains {} games'.format(url, gameList.attrib['AppVer'], gameList.attrib['TotalConfigurations']))
                    # date = 0 always gets update
                    if (int(gameList.attrib['Exported']) <= int(date) ):
                        logging.info('No updated game list available')
                    else:
                        for game in gameList.iter('Game'):
                            name = game.findtext('Name')
                            process = game.findtext('ProcessName')
                            isRegex = game.findtext('IsRegex', 'false')
                            parameter = game.findtext('Parameter', '')
                            monitorId = game.findtext('id', str(uuid.uuid4()))
                            absolutePath = game.findtext('AbsolutePath', 'false') == 'true'
                            folderSave = game.findtext('FolderSave', 'false') == 'true'
                            includeList = game.findtext('IncludeList', '')
                            excludeList = game.findtext('ExcludeList', '')
                            monitorOnly = game.findtext('MonitorOnly', 'false') == 'true'
                            comments = game.findtext('Comments', '')
                            self.addPlainGame(name, process, isRegex, parameter, monitorId, absolutePath, folderSave, includeList, excludeList, monitorOnly, comments)
                        logging.debug('Game list imported')
                        return gameList.attrib['Exported']
        except urllib.error.URLError:
            logging.error("{} is not accessible".format(url))
        return '0'