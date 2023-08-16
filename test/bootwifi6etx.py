import socket
from scapy.all import hexdump, raw, bytes_encode
from scapy.layers.l2 import Ether, Dot1Q
import time
from datetime import datetime, timedelta
import logging
import threading
import subprocess
import os
import realwlantraffic

wlanTrafficType = 'FTP'
ip_address = "192.168.1.1"
port = 50000
encoded = "\x02\x20\x0f\x01\xac\x10\x01\x06\x04\x01\x0e\x80\x00\x31\x02\x00\x30\x2d\x80\x01\x02\x81\x26\x00\x95\xb9\x6b\xfe\xff\xff\x35\xa4\xe9\x01\x6b\x49\xd2\x01\xf0\x00\xff\xff\xff\xff\xff\xff\x70\x80\x7f\x07\xd1\x07\xd1\x81\x7f\xff\x08\x00\x0c\x80\x32\xa3\x00\x70\x72\x65\x6d\x34\x34\x30\x30\x70\x72\x65\x6d\x70"

def countfiles():
    fcount=0
    for fname in os.listdir('/home/pi/owlbox_files/logs'):
        fpath=os.path.join('/home/pi/owlbox_files/logs',fname)
        if os.path.isfile(fpath):
            fcount+=1
    
    return fcount

doLog = False
if countfiles == 0:
    noLogFilePresent = True
else:
    noLogFilePresent = False

# Get the host name
host_name = socket.gethostname()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#s.bind(("wlan0", 0))

def dellogs():
    bash_cmd = f"rm -f /home/pi/owlbox_files/logs/*"
    try:
        subprocess.run(bash_cmd,shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error Occured: {e}")

changingChannel = False
def checkServer():
    global doLog
    global wlanTrafficType
    while True:
        cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('192.168.1.4', 8001)
        cs.sendto("checklog-{}".format(host_name).encode('utf-8'),server_address)
        cs.settimeout(.5)
        try:
            r = cs.recvfrom(1024)
        except:
            continue
        rm = r[0].decode('utf-8')
        rmarr = rm.split("-")
        if rmarr[0] == "log":
            doLog=True
            current_time = datetime.now().strftime('%m_%d_%Y_%H_%M')
            logging.basicConfig(filename="/home/pi/owlbox_files/logs/{}_{}.log".format(host_name,current_time), level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
            noLogFilePresent = False
        elif rmarr[0] == "nolog":
            doLog=False
        elif rmarr[0] == "logdeletealllogs":
            dellogs()
            current_time = datetime.now().strftime('%m_%d_%Y_%H_%M')
            logging.basicConfig(filename="/home/pi/owlbox_files/logs/{}_{}.log".format(host_name,current_time), level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
            noLogFilePresent = False
            doLog=True
        elif rmarr[0]=="nologdeletealllogs":
            doLog=False
            dellogs()
            noLogFilePresent = True
        
        wlanTrafficType = rmarr[1]
        time.sleep(1)

x = threading.Thread(target=checkServer)
x.start()
while True:
    try:
        #print(wlanTrafficType)
        payload = ''.encode()
        payloadDelay = 0
        o = (payload,payloadDelay)
        if wlanTrafficType=="FTP":
            o = realwlantraffic.trafficFTP()
            payload = o[0]
            payloadDelay = o[1]
        elif wlanTrafficType=="VIDEOCONF":
            o = realwlantraffic.videoConferencing()
            payload = o[0]
            payloadDelay = o[1]
        elif wlanTrafficType=="WEB":
            o = realwlantraffic.webBrowsing()
            payload = o[0]
            payloadDelay = o[1]
        elif wlanTrafficType=="FULL_RATE_FIXED_LEN":
            #print(changingChannel)
            payload = encoded
            payloadDelay = 0
            o = (payload,payloadDelay)
        else:
            print('Why are we here?')
        
        #print((len(o[0]),o[1]))
        #print(wlanTrafficType)
        time.sleep(payloadDelay/1000)
        s.sendto(payload,(ip_address, port))
            
        if doLog:
            logging.debug("{}-{}".format(len(payload),wlanTrafficType))
        # Get the current date and time
        #current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Combine the host name and date-time into a string
        #message = f"{host_name},{current_time}"
        # Send the message to the server
        #client_socket.sendall(message.encode())
        #time.sleep(.000001)
    except:
        continue
# Close the socket
#client_socket.close()
