#set_get_clock.py
# 
#Project: Dungeon Music Closer V3 - Terri Talton 2026
#
#This file gets NPT or RTC time and sets system clock if necessary

#Constants
configFile = '/home/terri/Documents/Dungeon music closer 2/Dungeon Closer thumb drive/config.cfg'  #TODO set appropriate for actual config file

#Imports
import time
import datetime
import subprocess
import time
import os
import struct
import ntplib
from configobj import ConfigObj
import logging

#Constants
config = ConfigObj(configFile)
log = logging.getLogger(config['logging']['level'])

#EndCom = "\xff\xff\xff"
#Defs:
def getNTPTime(): #Get internet time from NTP server
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org')
        os.system('sudo date ' + time.strftime('%m%d%H%M%Y.%S',time.localtime(response.tx_time)))
        netdate = (time.strftime('%m%d%H%M%Y.%S',time.localtime(response.tx_time)))
        netmonth = (time.strftime('%m',time.localtime(response.tx_time)))
        netday = (time.strftime('%d',time.localtime(response.tx_time)))
        netyear = (time.strftime('%Y',time.localtime(response.tx_time)))
        nethour = (time.strftime('%H',time.localtime(response.tx_time)))
        netminute = (time.strftime('%M',time.localtime(response.tx_time)))
        netsecond = (time.strftime('%S',time.localtime(response.tx_time)))
        setPiTime(netsecond,netminute,nethour,netmonth,netday,netyear)
    except:
        log.error("Failed to get NTP time")
        #getNextionTime() #Failed to get internet time.  Use RTC.  #TODO add get RTC time here

#def getRTCTime  #Get the time from the Real Time Clock  #TODO sdd get rtc time routine

def setPiTime(second,minute,hour,month,day,year):  #Set the system time and date
    #now = datetime.datetime.now()
    #print now.year, now.month, now.day, now.hour, now.minute, now.second
    mytime = str(year).zfill(4) + str(month).zfill(2) + str(day).zfill(2) + " " +str(hour).zfill(2) + ":" + str(minute).zfill(2) + ":" + str(second).zfill(2)
    log.debug(mytime)
    log.debug('old time: ' + time.strftime('%m%d%H%M%Y.%S'))
    subprocess.call('sudo date --set='+ '"' + mytime + '"',shell=True)
    log.debug('New time: ' + time.strftime('%m%d%H%M%Y.%S'))


#Main routine  #TODO Remove main routine from timeGetSet
#getNTPTime()  #Attempt to get internet time
