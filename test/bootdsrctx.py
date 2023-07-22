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

# TCP server details
#server_address = ('192.168.1.3', 4030)

#try:
    # Create a TCP socket
#    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the TCP server
#    client_socket.connect(server_address)

#except ConnectionRefusedError:
#    print("Connection to the server failed.")

t_cam = "\xFF\xFF\xFF\xFF\xFF\xFF\x74\xE5\x43\xD5\xFD\xA4\x89\x47\x01\x00\xF1\x01\x20\x50\x02\x74\x00\x2D\x01\x00\x95\xF9\x74\xE5\x43\xD5\xFD\xA4\xA7\x84\x11\x99\x19\x54\x08"

t_cam2 = "\x02\x20\x0f\x01\xac\x10\x01\x0c\x04\x01\x05\x80\x00\x31\x02\x00\x30\x2d\x80\x01\x02\x81\x26\x14\x80\x22\x22\x0e\x8f\xc0\x14\x2a\x28\x27\xcd\x94\xdc\x70\x0a\xb9\xff\xff\xff\xff\xe0\x02\x70\x80\x7f\x00\x08\x07\xd1\x81\x7f\xff\x08\x00\x0c\x80\x32\xa3\x00"

t_cam3 = "\xc3\xbf\xc3\xbf\xcf\xbf\x74\xE5\x43\xD5\xFD\xA4"

t_cam5 = "\x02\x20\x0f\x01\xac\x10\x01\x06\x04\x01\x0e\x80\x00\x31\x02\x00\x30\x2d\x80\x01\x02\x81\x26\x00\x95\xb9\x6b\xfe\xff\xff\x35\xa4\xe9\x01\x6b\x49\xd2\x01\xf0\x00\xff\xff\xff\xff\xff\xff\x70\x80\x7f\x07\xd1\x07\xd1\x81\x7f\xff\x08\x00\x0c\x80\x32\xa3\x00\x70\x72\x65\x6d\x34\x34\x30\x30\x70\x72\x65\x6d\x70"
#t_cam5 = t_cam5.enc(ASN1_Codecs.BER)

data = t_cam5
pkt = Ether()
pkt[Ether].dst = "ff:ff:ff:ff:ff:ff"
pkt[Ether].src = "7c:e9:3:51:86:6e"
pkt[Ether].type = 0x88dc
pkt = pkt/data
#pkt = #pkt/"\x02\x20\x0f\x01\xac\x10\x01\x06\x04\x01\x0e\x80\x00\x31\x02\x00\x30\x2d\x80\x01\x02\x81\x26\x00\x95\xb9\x6b\xfe\xff\xff\x35\xa4\xe9\x01\x6b\x49\xd2\x01\xf0\x00\xff\xff\xff\xff\xff\xff\x70\x80\x7f\x07\xd1\x07\xd1\x81\x7f\xff\x08\x00\x0c\x80\x32\xa3\x00"
#pkt = pkt/"\x02\x20\x0f\x01\xac\x10\x01\x06\x04\x01\x0e\x80\x00\x31\x02\x00\x30\x2d\x80\x01\x02\x81\x26\x00\x95\xb9\x6b\xfe\xff\xff\x35\xa4\xe9\x01\x6b\x49\xd2\x01\xf0\x00\xff\xff\xff\xff\xff\xff\x70\x80\x7f\x07\xd1\x07\xd1\x81\x7f\xff\x08\x00\x0c\x80\x32\xa3\x00"

s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
s.bind(("wlan0", 0))
# We're putting together an ethernet frame here, 
# but you could have anything you want instead
# Have a look at the 'struct' module for more 
# flexible packing/unpacking of binary data
# and 'binascii' for 32 bit CRC
#src_addr = "\x7C\xE9\x03\x51\x86\x6E"
#dst_addr = "\xFF\xFF\xFF\xFF\xFF\xFF"
#payload = ("["*30)+"PAYLOAD"+("]"*30)
#checksum = "\x1a\x2b\x3c\x4d"
#ethertype = "\x88\xDC"
#message = dst_addr+src_addr+ethertype+payload
encoded = bytes_encode(pkt)

def dellogs():
    bash_cmd = f"rm -f /home/pi/owlbox_files/logs/*"
    try:
        subprocess.run(bash_cmd,shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error Occured: {e}")

changingChannel = False
def checkServer():
    global doLog
    global changingChannel
    global wlanTrafficType
    ch='5885'
    chbw='20'
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
        #print(wlanTrafficType)
        server_address_chnum = ('192.168.1.4', 8002)
        cs.sendto("txparams-{}".format("channelnum").encode('utf-8'),server_address_chnum)
        cs.settimeout(.5)
        try:
            r = cs.recvfrom(1024)
        except:
            continue
        rm = r[0].decode('utf-8')
        
        arr = rm.split("-")  
        #print(arr)
        if arr[0]==ch and arr[1]==chbw:
            continue
        else:
            ch=arr[0]
            chbw=arr[1]
            changingChannel = True
            cmd = 'ip link set wlan0 down'
            os.system(cmd)
            time.sleep(.1)
            cmd = 'iw dev wlan0 set type ocb'
            os.system(cmd)
            time.sleep(.1)
            cmd = 'iw reg set US'
            os.system(cmd)
            time.sleep(.1)
            cmd = 'ip link set wlan0 up'
            os.system(cmd)
            time.sleep(.1)
            cmd = 'iw dev wlan0 ocb join %s %sMHZ' % (arr[0],arr[1])
            #print(cmd)
            os.system(cmd) 
            #cmd = 'iw wlan0 info'
            #os.system(cmd)
            time.sleep(.1)
        changingChannel = False
        time.sleep(1)

x = threading.Thread(target=checkServer)
x.start()
while True:
    if not changingChannel:
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
        s.send(payload)
        
    if doLog:
     logging.debug("{}-{}".format(len(payload),wlanTrafficType))
    # Get the current date and time
    #current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Combine the host name and date-time into a string
    #message = f"{host_name},{current_time}"
    # Send the message to the server
    #client_socket.sendall(message.encode())
    #time.sleep(.000001)

# Close the socket
#client_socket.close()
