#!/usr/bin/python3
#regex
import re;
#track processes
import psutil;
import time;
import datetime;
#linux notifications
import notify2;
notify2.init('gamesPy');
print('Listening for newly started games...');

trackedGames = {
    'SuperTux 2': {'processes': (
        {'name': 'supertux2'},
    )},
    'MegaGlest': {'processes': (
        {'name': 'megaglest'},
    )},
    'Xonotic': {'processes': (
        {'name': 'xonotic-glx'},
        {'name': 'xonotic-sdl'},
    )},
    'Beneath a Steel Sky': {'processes': (
        {'name': 'scummvm', 'argument': 'sky'},
    )},
    'Ardentryst': {'processes': (
        {'name': 'python2', 'argument': 'ardentryst.py'},
    )},
    'Shattered Pixel Dungeon': {'processes': (
        {'name': 'java', 'argument': 'shattered-pixel-dungeon.jar'},
    )},
    'Zelda Mystery of Solarus DX': {'processes': (
        {'name': 'solarus-run', 'argument': 'zsdx'},
    )},
    'Zelda Mystery of Solarus XD': {'processes': (
        {'name': 'solarus-run', 'argument': 'zsxd'},
    )},
    'Stealth Bastard Deluxe': {'processes': (
        {'name': 'runner', 'steamAppId': '209190'},
    )},
    'Antichamber': {'processes': (
        {'name': 'UDKGame-Linux', 'steamAppId': '219890'},
    )},
    #.exe
    'System Shock 2 Alt': {'processes': (
        {'name': 'Shock2'},
    )},
}

found = {'pid': -1, 'name': '', 'started': 0}
binaryExtension = '(.(exe|run|bin(.x86(_64)?)?|x86(_64)?))?';


def note(head, msg):
    notify2.Notification(head, msg).show();
    print(head + ":\n  " + msg);

def track():
    try:
        while 1:
            for proc in psutil.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time', 'cwd', 'cmdline', 'environ'])
                except psutil.NoSuchProcess:
                    pass
                else:
                    for name, game in trackedGames.items():
                        for trackedProcess in game['processes']:
                            #check if name is the same
                            #if set also check argument
                            if re.match('.*' + trackedProcess['name'] + binaryExtension, pinfo['name'])  and ( ('argument' not in trackedProcess) or (trackedProcess['argument'] in pinfo['cmdline'])):
                                found['pid'] = pinfo['pid'];
                                found['name'] = name;
                                found['startedu'] = pinfo['create_time'];
                                note(name + ' started', 'Has PID {pid} and was started {start}'.format(pid=pinfo['pid'],start=datetime.datetime.fromtimestamp(pinfo['create_time']).strftime("%Y-%m-%d %H:%M:%S")));
                                break;
                        if found['pid'] != -1:
                            break
                    if found['pid'] != -1:
                        break;
            while found['pid'] != -1:
                try:
                    p = psutil.Process(found['pid']);
                    pinfo = p.as_dict(attrs=['pid', 'name', 'create_time', 'cwd', 'cmdline', 'environ'])
                except psutil.NoSuchProcess:
                    note(found['name'] + " closed", 'Ended {end}'.format(end=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")));
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
        print('Good bye');

track();
