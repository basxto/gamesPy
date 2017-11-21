#!/usr/bin/python3
import os;
import sys;
import argparse;
import socket;#for hostname
#regex
import re;
#track processes
import psutil;
import time;
import datetime;
import configparser;
import sqlite3;
if sys.platform.startswith('linux'):
    #notifications
    import notify2;
    notify2.init('gamesPy');
    #follow XDG standard
    from xdg.BaseDirectory import xdg_config_home, xdg_data_home

class Game:
    def __init__(self, name, process, argument='', hours=0.0, monitorid=-1):
        self.name = name;
        self.process = process;
        self.argument = argument;
        self.hours = hours;
        self.monitorid = monitorid;
        self.sessions = [];
    def isProcess(self, pinfo):
        #check process name
        binaryExtension = '(\.(exe|run|elf|bin))?(\.(x86(_64)?|(amd|x)64))?';
        name = re.compile(self.process + binaryExtension + '$');
        if( not (pinfo['name'] and name.search(pinfo['name']) )
        and not (pinfo['exe' ] and name.search(pinfo['exe' ]) )):
            return False;
        # No argument is always contained
        if not self.argument:#!!!
            return True;
        #compare argument with every cmdline argument
        argument = re.compile(self.argument);
        if [arg for arg in pinfo['cmdline'] if argument.search(arg)]:
            return True;
        else:
            return False;
    def addSession(self, session):
        self.sessions.append(session);
    #Returns time delta
    def getPlaytime(self):
        timeAccu = datetime.timedelta();
        for session in self.sessions:
            timeAccu += session.getDuration();
        return timeAccu;

class Session:
    def __init__(self, game, start, end):
        self.game = game;
        self.start = start;
        self.end = end;
    #returns a time delta
    def getDuration(self):
        return self.end-self.start;

class Storage:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row;
        self.createDatabase();
    def createDatabase(self):
        #compatible to GBM v1.04
        cur = self.conn.cursor();
        cur.execute('''CREATE TABLE IF NOT EXISTS `sessions` (
                        `MonitorID` TEXT NOT NULL,
                        `Start` INTEGER NOT NULL,
                        `End` INTEGER NOT NULL,
                        `ComputerName` TEXT NOT NULL,
                        PRIMARY KEY(MonitorID, Start)
                    )''');
        cur.execute('''CREATE TABLE IF NOT EXISTS `monitorlist` (
                        `MonitorID`     TEXT    NOT NULL UNIQUE,
                        `Name`          TEXT    NOT NULL,
                        `Process`       TEXT    NOT NULL,
                        `Path`          TEXT,
                        `AbsolutePath`  BOOLEAN NOT NULL,
                        `FolderSave`    BOOLEAN NOT NULL,
                        `FileType`      TEXT,
                        `TimeStamp`     BOOLEAN NOT NULL,
                        `ExcludeList`   TEXT    NOT NULL,
                        `ProcessPath`   TEXT,
                        `Icon`          TEXT,
                        `Hours`         REAL,
                        `Version`       TEXT,
                        `Company`       TEXT,
                        `Enabled`       BOOLEAN NOT NULL,
                        `MonitorOnly`   BOOLEAN NOT NULL,
                        `BackupLimit`   INTEGER NOT NULL,
                        `CleanFolder`   BOOLEAN NOT NULL,
                        `Parameter`     TEXT,
                        `Comments`      TEXT,
                        PRIMARY KEY(`Name`, `Process`)
                    );''');
        cur.close();
    def readGames(self, trackedGames):
        cur = self.conn.cursor();
        cur.execute('SELECT `MonitorID`, `Name`, `Process`, `Parameter`, `Hours` FROM `monitorlist`');
        for row in cur:
            trackedGames[row["MonitorID"]] = Game(row["Name"], row["Process"], row["Parameter"], row["Hours"], row["MonitorID"]);
        cur.execute('SELECT `MonitorID`, `Start`, `End` FROM `sessions`');
        for row in cur:
            trackedGames[row["MonitorID"]].addSession(Session(trackedGames[row["MonitorID"]], datetime.datetime.fromtimestamp(row["Start"]), datetime.datetime.fromtimestamp(row["End"])));
        cur.close();
    def addSession(self, session):
        #use connection as a context manager
        try:
            with self.conn:
                self.conn.execute('INSERT INTO `sessions` (`MonitorID`, `Start`, `End`, `ComputerName`) VALUES (?, ?, ?, ?)',
                (session.game.monitorid, session.start.timestamp(), session.end.timestamp(), socket.gethostname()));
        except sqlite3.IntegrityError:
            print("Couldn't add session to database"); 
        print('INSERT INTO `sessions` (`MonitorID`, `Start`, `End`, `ComputerName`) VALUES ({}, {}, {}, {})'.format(session.game.monitorid, session.start.timestamp(), session.end.timestamp(), socket.gethostname()))
    def changeGame(self, game):
        try:
            with self.conn:
                self.conn.execute('UPDATE `monitorlist` SET `Hours` = ?  WHERE `MonitorID` = ?', (game.hours, game.monitorid));
        except sqlite3.IntegrityError:
            print("Couldn't change game in database")
        print('UPDATE `monitorlist` SET `Hours` = {}  WHERE `MonitorID` = {}'.format(game.hours, game.monitorid));

def note(head, msg):
    if sys.platform.startswith('linux'):
        notify2.Notification(head, msg).show();
    print(head + ":\n  " + msg);

def track(trackedGames):
    if not trackedGames:
        print('Empty game list...');
        return
    print('{} games are known'.format(len(trackedGames)));
    print('Listening for newly started games...');
    try:
        found = {'pid': -1, 'game': '', 'started': 0}
        while 1:
            for proc in psutil.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'exe', 'create_time', 'cwd', 'cmdline', 'environ'])
                except psutil.NoSuchProcess:
                    pass;
                else:
                    for monitorid, game in trackedGames.items():
                        #check if name is the same
                        #if set also check argument
                        if game.isProcess(pinfo):
                            found['pid'] = pinfo['pid'];
                            found['game'] = game;
                            found['startedu'] = pinfo['create_time'];
                            note(game.name + ' started', 'Has PID {pid} and was started {start}'.format(pid=pinfo['pid'],start=datetime.datetime.fromtimestamp(pinfo['create_time']).strftime("%Y-%m-%d %H:%M:%S")));
                            break;
                        if found['pid'] != -1:
                            break
                    if found['pid'] != -1:
                        break;
            #wait for running process
            while found['pid'] != -1:
                try:
                    p = psutil.Process(found['pid']);
                    pinfo = p.as_dict(attrs=['pid', 'name', 'create_time', 'cwd', 'cmdline', 'environ'])
                except psutil.NoSuchProcess:
                    tmpSession = Session(found['game'], datetime.datetime.fromtimestamp(pinfo['create_time']), datetime.datetime.now());
                    note(found['game'].name + " closed", 'Ended {end}'.format(end=tmpSession.start.strftime("%Y-%m-%d %H:%M:%S")));
                    print('This session of {} took {}h {}min {}sec'.format(found['game'].name, round((tmpSession.getDuration().seconds/3600)%24),round((tmpSession.getDuration().seconds/60)%60),tmpSession.getDuration().seconds%60));
                    found['game'].addSession(tmpSession);
                    if not args.dry_run:
                        storage.addSession(tmpSession);
                    print('You played {} {}h {}min {}sec in total'.format(found['game'].name, round((found['game'].getPlaytime().seconds/3600)%24),round((found['game'].getPlaytime().seconds/60)%60),found['game'].getPlaytime().seconds%60));
                    found['pid'] = -1;
                else:
                    try:
                        #wait for process to exit or 5 seconds
                        p.wait(5);
                    except psutil.TimeoutExpired:
                        pass;
            time.sleep(10);
    except KeyboardInterrupt:
        print('\nStopped listening for newly started games...');

def main():
    #command line arguments
    parser = argparse.ArgumentParser();
    parser.add_argument("--db", help="Path to sqlite3 database");
    parser.add_argument("--config", help="Path to config file");
    parser.add_argument("--dry-run", action='store_true', help="Don't modify the database");
    global args;
    args = parser.parse_args();
    
    # default is current directory
    configdir = '';
    datadir = '';
    if sys.platform.startswith('linux'):
        configdir = xdg_config_home + '/gamesPy/';
        datadir = xdg_data_home + '/gamesPy/';
    if configdir and not os.path.exists(configdir):
        os.makedirs(configdir);
    if datadir and not os.path.exists(datadir):
        os.makedirs(datadir);

    # default configurations
    config = configparser.ConfigParser();
    config['DATABASE'] = {'path': datadir + 'gamesPy.s3db'};
    # read and writeback configurations, writes defaults if not set
    config.read(args.config if args.config else configdir + 'gamesPy.ini');
    # command line argument has priority
    with open(configdir + 'gamesPy.ini', 'w+') as configfile:
        config.write(configfile);
    # command line argument has priority
    global storage;
    storage = Storage(args.db if args.db else config['DATABASE']['path']);
    trackedGames = {};
    storage.readGames(trackedGames);
    track(trackedGames);
    print('Good bye');

main();
