from network import LoRa
import socket
import time
import binascii
import struct
import math
import pycom
from machine import Timer
from network import WLAN

wlan = WLAN(mode=WLAN.STA)
lora = LoRa(mode=LoRa.LORAWAN)
app_eui = binascii.unhexlify('70B3D57ED0009786')
app_key = binascii.unhexlify('BA729441A1AD751B0F2C7238E23BA747')

lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')
pycom.heartbeat(False)
# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

def send_data(bssids):
    s.setblocking(True)
    s.bind(1)
    datastring = b''
    for bssid in bssids:
        #datastring += str(bssid, "utf-8")
        print('bssid : {}'.format(binascii.hexlify(bssid)))
        datastring += bssid
    #s.send(bytes([1, 0, pin_data, 2, 103]) + struct.pack('>h', int(temperature * 10)))
    #print('datastring {}'.format(datastring))
    #s.send(struct.pack('>36c', datastring))
    print("Sending data")
    s.send(datastring)
    s.setblocking(False)
    data = s.recv(64)
    if data:
        print("recvd data: {}".format(data))
        if data == b'\x01':
            pycom.rgbled(0x007f00)
        elif data == b'\x00':
            pycom.rgbled(0x000000)

def timerCallback(timer):
    nets = wlan.scan()
    #print(nets)
    bssids = []
    for net in nets:
        #bssids.append(binascii.hexlify(net.bssid))
        bssids.append(net.bssid)
        if len(bssids) == 3:
            break
    #print('bssids: {}'.format(bssids))
    send_data(bssids)

timer = Timer.Alarm(timerCallback, 60, periodic=True)

while True:
    time.sleep(0.1)
