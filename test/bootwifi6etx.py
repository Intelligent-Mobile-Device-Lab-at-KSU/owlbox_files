import socket
import random
import string
from scapy.all import hexdump, raw, bytes_encode
from scapy.layers.l2 import Ether, Dot1Q
import time
from datetime import datetime, timedelta
import logging
import threading
import subprocess

# Set the destination IP address and port
ip_address = "8.8.8.8"
port = 5005

# Set the length of the UDP data packets
packet_length = 2300

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


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Generate random data of packet_length bytes
random_data = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase, k=packet_length)).encode()

sock.bind(("wlan0", 0))

traffictype = "video"

def dellogs():
    bash_cmd = f"rm -f /home/pi/owlbox_files/logs/*"
    try:
        subprocess.run(bash_cmd,shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error Occured: {e}")
    
def checkServer():
    global doLog
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
        if rm == "log":
            doLog=True
            current_time = datetime.now().strftime('%m_%d_%Y_%H_%M')
            logging.basicConfig(filename="/home/pi/owlbox_files/logs/{}_{}.log".format(host_name,current_time), level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
            noLogFilePresent = False
        elif rm == "nolog":
            doLog=False
        elif rm == "logdeletealllogs":
            dellogs()
            current_time = datetime.now().strftime('%m_%d_%Y_%H_%M')
            logging.basicConfig(filename="/home/pi/owlbox_files/logs/{}_{}.log".format(host_name,current_time), level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
            noLogFilePresent = False
            doLog=True
        elif rm=="nologdeletealllogs":
            doLog=False
            dellogs()
            noLogFilePresent = True
            
        time.sleep(1)

x = threading.Thread(target=checkServer)
x.start()
while True:
     # Send the UDP data packet to the destination
     sock.sendto(random_data, (ip_address, port))
     if doLog:
         logging.debug("{}-{}".format(len(encoded),traffictype))

# Close the socket
#sock.close()
