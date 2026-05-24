#startme.py
# 
#Project: Party music closer - Terri Talton 2025
#Project is to create device that generates announcements in music stream to bring an end to a party.
#
#This file is to set up logging, threading, and main loop


#Constants:
configFile = '/home/terri/Documents/Dungeon music closer 2/Dungeon Closer thumb drive/config.cfg'  #TODO set appropriate for actual config file
logFile = '/home/terri/Documents/Dungeon music closer 2/Dungeon Closer thumb drive/log.log'  #TODO set appropriate for actual log file

#Imports
import subprocess
import socket
from configobj import ConfigObj
import time
config = ConfigObj(configFile)
import logging
import timeGetSet

#Logging
from logging.handlers import RotatingFileHandler
LOG_FILENAME = logFile  # Like, the log file, man.
# Set up a specific logger with our desired output level
logging.basicConfig(level=config['logging']['level'], filemode="w")
log = logging.getLogger(config['logging']['level'])


# Add the log message handler to the logger
#handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=100000, backupCount=5, )
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, backupCount=5, )
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.handlers[0].doRollover()
log.addHandler(logging.StreamHandler())


#Defs:
def internet_on(): #Check to see if we have an internet connection
    REMOTE_SERVER = 'www.google.com'

    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(REMOTE_SERVER)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)

        return True
    except:
        pass
        return False
            

def startup():
        if internet_on():
            log.debug('INTERNET ON (startme)')
            timeGetSet.getNTPTime()
        else:
            log.debug('INTERNET OFF (startme)')
        #TODO Initialize display variables
        #TODO Get calendar entries from offline
        #TODO process calendar entries into alarm DB

#Main routine
log.info('starting')
try:
    #subprocess.call(['sudo','pulseaudio', '-D', '--system'])
    #TODO initialize audio
    pass
except OSError as e:
        log.warning(e.output) #Oh shit!  We hit an error!  Dive! Dive! Dive!

if __name__ == '__main__':  

    startup()