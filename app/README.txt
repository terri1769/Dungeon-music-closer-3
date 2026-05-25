#README.txt
# 
#Project: Close-o-matic - Terri Talton 2025

This project stemmed from a need to kick people out of a party.
This was for a convention where there are regularly timed parties in a single space
The device drops the sound and makes closing announcements at regular intervals
Then it brings the sound back up until the next interval.
At the end of the party, it drops sound, makes a final announcement then starts a close playlist
We found playing obnoxious music that no one wanted to listen to was effective at clearing the room.

Prior to the event, use either in-built web interface, or spreadsheet editor for offline use, to enter all details for parties
The device then uses APScheduler to fire alarms as needed.  Config file contains the time offsets for when to fire pre-close announcements.
Such as 30 minutes before, 15 minutes before, 5 minutes before, etc.  It also includes the actual messages to be read by TTS.
The thumb drive with the config file also includes the play list for the after-close announcement.  
#TODO determine what types of input are available and document

Device includes display to allow changing input and voice volumes along with other parameters.  #TODO determine what's on screen and document
Master volume will be controlled by a knob.  #TODO determine id potentiometer or rotary encoder

Device includes an MP3 interface module to handle inputs.  Aux, TF card, Thumb Drive, and Bluetooth.  Processing is agnostic of input types


Prerequisites:
Python 3 virtual environment

From pip3:
APScheduler
configobj
ntplib


Hardware:
Raspberry Pi 5, 4GB.  Boots from either NVME, with microd SD card as emergency backup (cloned)
Boots Raspberry Pi OS Lite 64bit
Audioinjector Zero Raspberry Pi Sound Card.  https://www.audioinjector.net/rpi-zero
Display  Rasoberry Pi 7" DSI display
Thumb drive for close music and config
Real Time Clock module with battery backup built in to Pi 5
    

Instructions for use:
