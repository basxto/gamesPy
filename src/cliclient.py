#!/usr/bin/python3
import os
import sys
import argparse
import logging
import configparser
if sys.platform.startswith('linux'):
    # follow XDG standard
    from xdg.BaseDirectory import xdg_config_home, xdg_data_home

import requests

def stringToBool(str):
    return ( str.upper() == 'YES' or str.upper() == 'TRUE' or str.upper() == 'ON' )

def main():
    #command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-games", help="List all games")
    parser.add_argument("--game-info", help="Detailed information for specified game")
    #parser.add_argument("--xmlimport", help="URL of xml game list")
    #parser.add_argument("--update", help="Update games list from official website")
    parser.add_argument("--log", default="WARNING", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    parser.add_argument("--port", default="6435", help="Port of server")#64M35
    #parser.add_argument("--dry-run", action='store_true', help="Don't modify the database") #TODO
    global args
    args = parser.parse_args()
    
    # default is current directory
    configdir = ''
    datadir = ''
    # set default paths and create directories
    if sys.platform.startswith('linux'):
        configdir = xdg_config_home + '/gamesPy/'
        datadir = xdg_data_home + '/gamesPy/'
    if configdir and not os.path.exists(configdir):
        os.makedirs(configdir)
    if datadir and not os.path.exists(datadir):
        os.makedirs(datadir)
    # configure logging
    # loglevel defaults to warning if input is incorrect 
    logging.basicConfig(
        filename=datadir+'gpy-cli.log',
        format='[%(asctime)s] %(levelname)s:%(message)s',
        level=getattr(logging, args.log.upper(), logging.WARNING)
    )
    if args.list_games and stringToBool(args.list_games):
        games = requests.get('http://127.0.0.1:6435/game/list').json()
        for id in games:
            print('{} (ID: {})'.format(games[id], id))
    elif args.game_info:
        id = args.game_info
        game = requests.get('http://127.0.0.1:6435/game/{}'.format(id)).json()
        print('Name: {}'.format(game['name']))
        print('Process name: "{}"'.format(game['process']))
        if game['argument'] != '':
            print('Arguments: "{}"'.format(game['argument']))
        print('You played this game {} hours {} minutes and {} seconds'.format(game['playTime']['hours'], game['playTime']['minutes'], game['playTime']['seconds']))
    else:
        #without arguments nothing happens
        parser.print_help()
main()