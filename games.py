#!/usr/bin/python3
import os;
import sys;
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
    sessions = [];
    def __init__(self, name, process, argument=''):
        self.name = name;
        self.process = process;
        self.argument = argument;
    def isProcess(self, pinfo):
        #check process name
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

trackedGames = [];

found = {'pid': -1, 'game': '', 'started': 0}
binaryExtension = '(\.(exe|run|elf|bin))?(\.(x86(_64)?|(amd|x)64))?';


def note(head, msg):
    if sys.platform.startswith('linux'):
        notify2.Notification(head, msg).show();
    print(head + ":\n  " + msg);

def createDatabase():
    #compatible to GBM v1.04
    cur = conn.cursor();
    cur.execute('''CREATE TABLE IF NOT EXISTS monitorlist (
                    MonitorID TEXT NOT NULL UNIQUE,
                    Name TEXT NOT NULL,
                    Process TEXT NOT NULL,
                    Path TEXT,
                    AbsolutePath BOOLEAN NOT NULL,
                    FolderSave BOOLEAN NOT NULL,
                    FileType TEXT,
                    TimeStamp BOOLEAN NOT NULL,
                    ExcludeList TEXT NOT NULL,
                    ProcessPath TEXT,
                    Icon TEXT,
                    Hours REAL,
                    Version TEXT,
                    Company TEXT,
                    Enabled BOOLEAN NOT NULL,
                    MonitorOnly BOOLEAN NOT NULL,
                    BackupLimit INTEGER NOT NULL,
                    CleanFolder BOOLEAN NOT NULL,
                    Parameter TEXT,
                    PRIMARY KEY(Name, Process)
                )''');
    cur.close();

def readGames():
    cur = conn.cursor();
    cur.execute('SELECT Name, Process, Parameter, Hours FROM monitorlist ORDER BY Hours DESC, Name ASC');
    for row in cur:
        trackedGames.append(Game(row["Name"],row["Process"],row["Parameter"]));
    cur.close();

def track():
    if not trackedGames:
        print('Empty game list...');
        return
    print('{} games are known'.format(len(trackedGames)));
    print('Listening for newly started games...');
    try:
        while 1:
            for proc in psutil.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'exe', 'create_time', 'cwd', 'cmdline', 'environ'])
                except psutil.NoSuchProcess:
                    pass
                else:
                    for game in trackedGames:
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
                    print('This session took {0}h {1}min {2}sec'.format(round((tmpSession.getDuration().seconds/3600)%24),round((tmpSession.getDuration().seconds/60)%60),tmpSession.getDuration().seconds%60));
                    found['game'].addSession(tmpSession);
                    print('You played this game {0}h {1}min {2}sec in total'.format(round((found['game'].getPlaytime().seconds/3600)%24),round((found['game'].getPlaytime().seconds/60)%60),found['game'].getPlaytime().seconds%60));
                    found['pid'] = -1;
                else:
                    try:
                        #wait for process to exit or 5 seconds
                        p.wait(5);
                    except psutil.TimeoutExpired:
                        pass;
            time.sleep(10);
    except KeyboardInterrupt:
        print('Stopped listening for newly started games...');

def main():
    # default is current directory
    configdir = ''
    datadir = ''
    if sys.platform.startswith('linux'):
        configdir = xdg_config_home + '/gamesPy/'
        datadir = xdg_data_home + '/gamesPy/'
    if configdir and not os.path.exists(configdir):
        os.makedirs(configdir)
    if datadir and not os.path.exists(datadir):
        os.makedirs(datadir)
    # default configurations
    config = configparser.ConfigParser();
    config['DATABASE'] = {'path': datadir + 'gamesPy.s3db'}
    # read and writeback configurations, writes defaults if not set
    config.read(configdir + 'gamesPy.ini')
    with open(configdir + 'gamesPy.ini', 'w+') as configfile:
        config.write(configfile)
    global conn
    conn = sqlite3.connect(config['DATABASE']['path'])
    conn.row_factory = sqlite3.Row;
    createDatabase()
    readGames();
    track();
    print('Good bye');

main();
