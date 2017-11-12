#!/usr/bin/python3 


import psutil;
#from pynoti import noti;
import time;
import datetime;
import notify2;
notify2.init('gamesPy');
print('Listening for newly started games...');

#~ trackedGames = (
	#~ {'name': 'MegaGlest', 'processes': (
		#~ {'name': 'megaglest'}
	#~ )},
	#~ {'name': 'Xonotic', 'processes': (
		#~ {'name': 'xonotic-glx'},
		#~ {'name': 'xonotic-sdl'}
	#~ )},
	#~ {'name': 'Beneath a Steel Sky', 'processes': (
		#~ {'name': 'scumvm', 'containArgument': 'sky'}
	#~ )},
#~ )
trackedGames = {
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
		{'name': 'java'},# 'argument': 'shattered-pixel-dungeon.jar'},
	)},
	'Zelda Mystery of Solarus DX': {'processes': (
		{'name': 'solarus-run'},#, 'argument': 'zsdx'},
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
}

#~ foundpid = -1
#~ foundname = ''
#~ foundstarted = 0
found = {'pid': -1, 'name': '', 'started': 0}
#for pid in psutil.pids():
#	p = psutil.Process(pid);
#	print(p.name());
#	print(p.cmdline());
try:
	while 1:
		for proc in psutil.process_iter():
			try:
				pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time', 'cwd', 'cmdline', 'environ'])
			except psutil.NoSuchProcess:
				pass
			else:
				#if pinfo['name'] == 'megaglest' or pinfo['name'] == 'scummvm' or pinfo['name'] == 'xonotic-glx':
				for name, game in trackedGames.items():
					for trackedProcess in game['processes']:
						if pinfo['name'] == trackedProcess['name'] and ( ('argument' not in trackedProcess) or (trackedProcess['argument'] in pinfo['cmdline'])):
							found['pid'] = pinfo['pid'];
							found['name'] = name;#pinfo['name'];
							found['startedu'] = pinfo['create_time'];
							notify2.Notification(name + ' started', 'Has PID ' + str(pinfo['pid']) + ' and was started ' + datetime.datetime.fromtimestamp(pinfo['create_time']).strftime("%Y-%m-%d %H:%M:%S")).show();
							break;
					if found['pid'] != -1:
						break
				if found['pid'] != -1:
					break;
		#        print(pinfo)
		#if foundpid != -1:
		while found['pid'] != -1:
			try:
				p = psutil.Process(found['pid']);
				pinfo = p.as_dict(attrs=['pid', 'name', 'create_time', 'cwd', 'cmdline', 'environ'])
				
			except psutil.NoSuchProcess:
				notify2.Notification(found['name'] + " closed").show();
				found['pid'] = -1;
			else:
				print(pinfo)
				#print(p.threads())
				#print(p.children())
				#print(p.open_files())
				#print(p.connections())
				for con in p.connections():
					if con.status == psutil.CONN_ESTABLISHED:
						print(con);
			#	print('found game "%s" with pid %d', p.name(), foundpid)
				#show a standard linux notification
				#notify2.Notification('found game "' + p.name() + '" with pid ' + str(foundpid), 'was started ' + datetime.datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S")).show();
				#time.sleep(20);
				try:
					#wait for process to exit or 5 seconds
					p.wait(5);
				except psutil.TimeoutExpired:
					pass;
		#noti.Noti("test title", "test message").run()
		time.sleep(10);
except KeyboardInterrupt:
	print('Stopped listening for newly started games...');
	print('Good bye');
