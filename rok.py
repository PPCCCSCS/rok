#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import subprocess
import logging

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
  
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
#import traceback

def readNetAuths(inFile):
    keyChain = []
    keyIndex = -1
         
    line = inFile.readline()
        
    while line != "":
        # Check for network={
        if "network" in line and "=" in line and "{" in line:
        # Create a new list entry
            keyIndex = keyIndex + 1
            keyChain.append(["","","",""])
            while "}" not in line:
                line = inFile.readline()
        #  Check for ssid="
                if "ssid=" in line:
                    keyChain[keyIndex][0] = line.split('"')[1]
                if "psk=" in line:
                    keyChain[keyIndex][1] = line.split('"')[1]
                if "key_mgmt=" in line:
                    line = line.strip()
                    keyChain[keyIndex][2] = line.split('=')[1]
                if "disabled=" in line:
                    line = line.strip()
                    keyChain[keyIndex][3] = line.split('=')[1]
        line = inFile.readline()
    return keyChain

def getNetAuth(ssid, keyChain):
    
    print(keyChain)
    
    netAuth = ["","","",""]
    
    for network in keyChain:
        if network[0] == ssid:
            netAuth[0] = network[0]
            netAuth[1] = network[1]
            if "WPA" in network[2]:
                netAuth[2] = "WPA"
            elif "WEP" in network[2]:
                netAuth[2] = "WEP"
            else:
                netAuth[2] = ""
            if network[3] == "1":
                netAuth[3] = "true"
            else:
                netAuth[3] = "false"
    
    return netAuth

def qrGen(entry, path):
    subprocess.call(["/usr/bin/qrencode","-l","L","-m","4","-o",os.path.join(path, entry[0]+".png"),"WIFI:S:"+entry[0]+";T:"+entry[2]+";P:"+entry[1]+";H:"+entry[3]+";"])
    subprocess.call(["/usr/bin/convert",os.path.join(path, entry[0]+".png"),"-alpha","Off","-resize","176x176","-depth","1",os.path.join(path, entry[0]+".bmp")])
 
def drawScreen(entry, path):
    epd = epd2in7.EPD()
    
    epd.init()
    epd.Clear(0xFF)
    
    centerW = epd.width/2
    centerH = epd.height/2
    
    font24 = ImageFont.truetype(os.path.join(path, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(path, 'Font.ttc'), 18)
    font35 = ImageFont.truetype(os.path.join(path, 'Font.ttc'), 35)
    
    if entry[0] == "":
        entry[0] = "<NONE>"
    
    if entry[1] == "":
        entry[1] = "<NONE>"
        
    display = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    bmp = Image.open(os.path.join(path, entry[0]+".bmp"))
    display.paste(bmp, (0,0))
    draw = ImageDraw.Draw(display)
    width, height = draw.textsize("SSID", font=font18)
    draw.text((centerW-(width/2), 170), "SSID", font = font18, fill = 0)
    width, height = draw.textsize(entry[0], font=font18)
    draw.text((centerW-(width/2), 190), str(entry[0]), font = font18, fill = 0)
    width, height = draw.textsize("PASSWORD", font=font18)
    draw.text((centerW-(width/2), 210), "PASSWORD", font = font18, fill = 0)
    width, height = draw.textsize(entry[1], font=font18)
    draw.text((centerW-(width/2), 230), entry[1], font = font18, fill = 0)
    epd.display(epd.getbuffer(display))
    time.sleep(2)

    epd.sleep()


def main():
    try:
        picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
        
        wpas = open("/etc/wpa_supplicant/wpa_supplicant.conf","r")
        
        netAuths = readNetAuths(wpas)
        
        ssid = subprocess.getoutput('iwgetid -r')

        lanKey = getNetAuth(ssid, netAuths).copy()
       
        qrGen(lanKey, picdir)
         
        drawScreen(lanKey, picdir)
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd2in7.epdconfig.module_exit()
        exit()

main()