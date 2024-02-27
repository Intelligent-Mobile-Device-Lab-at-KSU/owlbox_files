
import serial
import signal
import sys
import time
import threading
import pynmea2
import json
import math
from socket import socket, AF_PACKET, SOCK_RAW
from scapy.all import hexdump, raw, bytes_encode
from scapy.layers.l2 import Ether, Dot1Q
from scapy.sendrecv import sendp
from binascii import hexlify, unhexlify
import os
import saej2735_2016
dsrc = saej2735_2016.DSRC()

OwlBox_BSM = {
    "owlboxID": "BusBox1",
    "msgCnt": 54,
    "tempid": 1762,
    "time": 1630714938,
    "lat": 30.012,
    "long": -97.6025,
    "elev": 175,
    "accuracy": 506,
    "transmission": 7,
    "speed": 65,
    "heading": "N",
    "angle": 127,
    "accelSet": 9.19,
    "brakes": 0,
    "size": {
        "length": 191,
        "width": 76,
    },
}

# Example BSM PART I TEMPLATE ======================== 
msgCnt = 0
tmpid = b'0033'#bytearray([0,0,0,27]).encode('utf-8')
#tmpid = "{0:32}".format(int(os.uname()[1][-2:]))
#print(oct(int(os.uname()[1][-2:])))
#tmpid=oct(int(os.uname()[1][-2:]))
secMark = 0
lat = -900000000
long = -1799999999
elev = -4096
SemiMajorAxisAccuracy = 0
SemiMinorAxisAccuracy = 0
SemiMajorAxisOrientation = 0
transmission = 'unavailable'
speed = 8191
heading = 0
steeringangle = 127
accellongaxis = 2001 
accelllataxis = 2001
accellvert = -127
accelyaw = -32767
wheelbrakes = {'unavailable'}
traction = 'unavailable'
abs = 'unavailable'
scs = 'unavailable'
brakeboost = 'unavailable'
auxbrake = 'unavailable'
veh_width = 0
veh_length = 0

#print(MF_BSM.to_asn1())
s = socket(AF_PACKET, SOCK_RAW)
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

gga=False
rmc=False
vtg=False
o=''
pktNum = 0
ser = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=1)
while True:
    nmea_sentence = '-------'
    while len(nmea_sentence)>0:
        nmea_sentence = ser.readline().decode('utf-8')
        #print(nmea_sentence)
        if 'GGA' in nmea_sentence:
            msg_latlon=pynmea2.parse(nmea_sentence)
            o+="%s,%s"%(msg_latlon.latitude,msg_latlon.longitude)
            gga=True
        if 'RMC' in nmea_sentence:
            msg = pynmea2.parse(nmea_sentence)
            try:
                angle = float(msg.true_course)
                angle = 360+(90-angle)
                if angle > 360:
                    angle = angle - 360
                #print(angle)
            except:
                angle='127'
            o+="%s,"%(str(angle))
            rmc=True
        if 'VTG' in nmea_sentence:
            msg = pynmea2.parse(nmea_sentence)
            #print(math.ceil(((msg.spd_over_grnd_kmph * 1000)/3600)/.02))
            try:
                thespeed=math.ceil(((msg.spd_over_grnd_kmph * 1000)/3600)/.02)
            except:
                thespeed=8191
            o+="%s,"%thespeed
            vtg=True
                                                 
        if gga and rmc and vtg:
            #print(o)
            data = o.split(",")
            OwlBox_BSM["lat"] = float(data[2])
            OwlBox_BSM["long"] = float(data[3])
            OwlBox_BSM["angle"] = float(data[0])
            OwlBox_BSM["speed"] = int(data[1])
            #print(OwlBox_BSM)
            lats = data[2].replace('.','')
            lons = data[3].replace('.','')
            
            bstringlat = int(lats[:9])
            bstringlon = int(lons[:10])
            #print(bstringlat)
            #print(bstringlon)
            if 1:
                bsmp1 = {
                        'msgCnt': (msgCnt + 1) % 128,
                        'id': tmpid,
                        'secMark': secMark,
                        'lat': bstringlat,
                        'long': bstringlon,
                        'elev': elev,
                        'accuracy':
                            {
                                'semiMajor': SemiMajorAxisAccuracy,
                                'semiMinor': SemiMinorAxisAccuracy,
                                'orientation': SemiMajorAxisOrientation
                            },
                        'transmission': transmission,
                        'speed': int(data[1]),
                        'heading': math.ceil(float(data[0])/.0127),
                        'angle': steeringangle,
                        'accelSet':
                            {
                                'long': accellongaxis,
                                'lat': accelllataxis,
                                'vert': accellvert,
                                'yaw': accelyaw
                            },
                        'brakes': 
                            {
                                'wheelBrakes': wheelbrakes,
                                'traction': traction,
                                'abs': abs,
                                'scs': scs,
                                'brakeBoost': brakeboost,
                                'auxBrakes': auxbrake
                            },
                        'size':
                            {
                                'width': veh_width,
                                'length': veh_length
                            },
                        }

                bsmp1 = {
                    'coreData': bsmp1
                }
                MF_BSM = dsrc.MessageFrame
                bsm_mf = {
                    'messageId': 20,
                    'value': ('BasicSafetyMessage',bsmp1)
                }
                MF_BSM.set_val(bsm_mf)
                
                print(hexlify(MF_BSM.to_uper()).decode('ascii'))
            boxData = MF_BSM.to_uper()#json.dumps(OwlBox_BSM).encode('utf8')
            pkt = Ether()
            pkt[Ether].dst = "ff:ff:ff:ff:ff:ff"
            pkt[Ether].src = "d0:df:9a:6d:ef:ab"
            #"7c:e9:3:51:86:6e"
            pkt[Ether].type = 0x88dc
            pkt = pkt/boxData
            print(pkt)
            encoded = bytes_encode(pkt)
            sendp(pkt, iface="wlan0")
            #s.send(encoded)
            #print(encoded)
            #print('/n')
            pktNum = pktNum + 1
            o = ''
            gga=False
            rmc=False
            vtg=False            
            #ss.sendto(o.encode(),(destIP_udp,destPort_udp))
            o=''
    time.sleep(.1)
