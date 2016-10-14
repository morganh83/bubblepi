#!/bin/bash

# Set Path variable ----DO NOT DELETE THIS OR THE SCRIPT WILL NOT RUN ON BOOT
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/bubblePi

# Conf
. shell.conf

# launch audio stream --- if the audio is choppy, adjust the "ar" switch. 16k should be sufficient

avconv -f alsa -ac 1 -ar 16000 -i hw:1,0 -acodec libmp3lame -f rtp rtp://$listenIP:$listenPort 2>/var/log/audio.log &

# to listen to rtp stream, use open VLC Media Player, go to 'File' > 'Open Capture Device'. Select 'Network' > 'Open RTP/UDP' Stream.
# Select RTP radial button and Multicast. Set IP to 0.0.0.0 and the port used in the configuration file and select open.


# Launch video stream 
# Use browser pointed to this IP at 8080 to view video
mjpg_streamer -i "input_uvc.so -r 768x480 -f 15" -o "output_http.so -w /usr/www" &

# Launch SOCKS Proxy SSH Tunnel
# To view the cam feed, use the following on your local system: ssh -f -N -q -C -o 'StrictHostKeyChecking no' -o ServerAliveInterval=60 -D 8081 user@IP
ssh -R 8080:localhost:8080 -f -C -q -N -o 'StrictHostKeyChecking no' -o ServerAliveInterval=60 ${userName//[[:space:]]}@${reverseDest//[[:space:]]}
