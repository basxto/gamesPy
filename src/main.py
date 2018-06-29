#!/usr/bin/python3
import os
import sys
import argparse
import logging
import configparser
if sys.platform.startswith('linux'):
    # follow XDG standard
    from xdg.BaseDirectory import xdg_config_home, xdg_data_home

import tracking
import storage

def main():
    #command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", help="Path to sqlite3 database")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--xmlimport", help="URL of xml game list")
    parser.add_argument("--update", help="Update games list from official website")
    parser.add_argument("--log", default="WARNING", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    parser.add_argument("--dry-run", action='store_true', help="Don't modify the database") #TODO
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
        filename=datadir+'gpy.log',
        format='[%(asctime)s] %(levelname)s:%(message)s',
        level=getattr(logging, args.log.upper(), logging.WARNING)
    )
    print("Log file at {}".format(datadir+'gpy.log'), flush=True)
    # default configurations
    global config
    config = configparser.ConfigParser()
    config['DATABASE'] = {'path': datadir + 'gamesPy.s3db'}
    config['UPDATE'] = {
        'date': '0',
        'url': 'https://basxto.github.io/gbm-web/GBM_Official_Linux.xml',
    }
    config['RUN'] = {
        'onstart': '',
        'onquit': ''
    }
    # read and writeback configurations, writes defaults if not set
    config.read(args.config if args.config else configdir + 'gamesPy.ini')
    # command line argument has priority
    with open(configdir + 'gamesPy.ini', 'w+') as configfile:
        config.write(configfile)
    # command line argument has priority
    store = storage.Database(args.db if args.db else config['DATABASE']['path'], args.dry_run)
    trackedGames = {}
    if args.xmlimport:
        store.importGames(args.xmlimport)
    if args.update and ( args.update.upper() == 'YES' or args.update.upper() == 'TRUE' or args.update.upper() == 'ON' ):
        newDate = store.importGames(config['UPDATE']['url'], config['UPDATE']['date'])
        if int(newDate) > int(config['UPDATE']['date']):
            config['UPDATE']['date'] = newDate
        # update config file
        with open(configdir + 'gamesPy.ini', 'w+') as configfile:
            config.write(configfile)
    store.getGames(trackedGames)
    tracking.track(trackedGames, config, store)

main()