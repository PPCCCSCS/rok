#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import subprocess

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
ssid = subprocess.getoutput('iwgetid -r')
wifipw = ""
encrpt = ""
hidden = ""
keyChain = []
keyIndex = -1

if ssid == "":
    ssid = "<NONE>"
    
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
#import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("RPi QR Code WLAN SSID Display")
            
    wpas = open("/etc/wpa_supplicant/wpa_supplicant.conf","r")
    logging.info("Opened wpa_supplicant")
    
    line = wpas.readline()
    logging.info("read first line: " + line)
    
    while line != "":
        # Check for network={
        if "network" in line and "=" in line and "{" in line:
        # Create a new list entry
            logging.info("Found New Network Configuration")
            keyIndex = keyIndex + 1
            keyChain.append(["","","",""])
            while "}" not in line:
                line = wpas.readline()
        #  Check for ssid="
                if "ssid=" in line:
                    logging.info("Found SSID: " + line.split('"')[1])
                    keyChain[keyIndex][0] = line.split('"')[1]
                if "psk=" in line:
                    logging.info("Found PreShared Key: " + line.split('"')[1])
                    keyChain[keyIndex][1] = line.split('"')[1]
                if "key_mgmt=" in line:
                    line = line.strip()
                    logging.info("Found Key Management: " + line.split('=')[1])
                    keyChain[keyIndex][2] = line.split('=')[1]
                if "disabled=" in line:
                    line = line.strip()
                    logging.info("WLAN disabled = " + line.split('=')[1])
                    keyChain[keyIndex][3] = line.split('=')[1]
        line = wpas.readline()
        logging.info("Read next line: " + line)
    print(keyChain)

    for network in keyChain:
        if network[0] == ssid:
            wifipw = network[1]
            if "WPA" in network[2]:
                encrpt = "WPA"
            elif "WEP" in network[2]:
                encrpt = "WEP"
            else:
                encrpt = ""
            if network[3] == "1":
                hidden = "true"
            else:
                hidden = "false"
   
    epd = epd2in7.EPD()
        
    logging.info("init and Clear")
    epd.init()
    epd.Clear(0xFF)
    
    centerW = epd.width/2
    centerH = epd.height/2
        
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
    
    ## BLOCK BELOW IS VERY *NOT* FINAL CODE!
   
    subprocess.call(["/usr/bin/qrencode","-l","L","-m","4","-o",os.path.join(picdir, ssid+".png"),"WIFI:S:"+ssid+";T:"+encrpt+";P:"+wifipw+";H:"+hidden+";"])
    subprocess.call(["/usr/bin/convert",os.path.join(picdir, ssid+".png"),"-alpha","Off","-resize","176x176","-depth","1",os.path.join(picdir, ssid+".bmp")])
    
    if wifipw == "":
        wifipw = "<NONE>"
  
    logging.info("4.read bmp file on window")
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    bmp = Image.open(os.path.join(picdir, ssid+".bmp"))
    Himage.paste(bmp, (0,0))
    draw = ImageDraw.Draw(Himage)
    width, height = draw.textsize("SSID", font=font18)
    draw.text((centerW-(width/2), 170), "SSID", font = font18, fill = 0)
    width, height = draw.textsize(ssid, font=font18)
    draw.text((centerW-(width/2), 190), ssid, font = font18, fill = 0)
    width, height = draw.textsize("PASSWORD", font=font18)
    draw.text((centerW-(width/2), 210), "PASSWORD", font = font18, fill = 0)
    width, height = draw.textsize(wifipw, font=font18)
    draw.text((centerW-(width/2), 230), wifipw, font = font18, fill = 0)
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)

#    logging.info("Clear...")
#    epd.Clear(0xFF)
    
    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in7.epdconfig.module_exit()
    exit()
