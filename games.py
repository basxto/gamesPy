#!/usr/bin/python3
import os;
#regex
import re;
#track processes
import psutil;
import time;
import datetime;
import configparser
#linux notifications
import notify2;
notify2.init('gamesPy');
#follow XDG standard on Linux
from xdg.BaseDirectory import xdg_config_home, xdg_data_home

class Game:
    sessions = [];
    def __init__(self, name, process, argument=''):
        self.name = name;
        self.process = process;
        self.argument = argument;
    def isProcess(self, pinfo):
        #check process name
        name = re.compile(self.process + binaryExtension);
        if( not (pinfo['name'] and name.search(pinfo['name']) )
        and not (pinfo['exe' ] and name.search(pinfo['exe' ]) )):
            return False;
        # No argument is always contained
        if self.argument:
            return True;
        #compare argument with every cmdline argument
        argument = re.compile(self.argument + '$');
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

trackedGames = [
    Game('SuperTux 2', 'supertux2'),
    Game('MegaGlest', 'megaglest'),
    Game('Xonotic', 'xonotic-(glx|sdl)'),
    Game('Beneath a Steel Sky', 'scummvm', 'sky'),
    Game('Ardentryst', 'python2', 'ardentryst.py'),
    Game('Shattered Pixel Dungeon', 'java', 'shattered-pixel-dungeon.jar'),
    Game('Zelda Mystery of Solarus DX', 'solarus-run', 'zsdx'),
    Game('Zelda Mystery of Solarus XD', 'solarus-run', 'zsxd'),
    Game('Stealth Bastard Deluxe', 'runner'),
    Game('Antichamber', 'UDKGame-Linux'),
    Game('System Shock 2', 'Shock2')
];

sessions = [];

found = {'pid': -1, 'game': '', 'started': 0}
binaryExtension = '(\.(exe|run|elf|bin))?(\.(x86(_64)?|(amd|x)64))?$';


def note(head, msg):
    notify2.Notification(head, msg).show();
    print(head + ":\n  " + msg);

def track():
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
    config = configparser.ConfigParser();
    configdir = xdg_config_home + '/gamesPy/'
    config.read(configdir + '/gamesPy.ini')
    if not os.path.exists(configdir):
        os.makedirs(configdir)
    with open(configdir + '/gamesPy.ini', 'w+') as configfile:
        config.write(configfile)
    track();
    print('Good bye');

main();
