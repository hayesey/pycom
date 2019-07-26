from network import LoRa
import socket
import time
import binascii
import struct
import pycom
#from deepsleep import DeepSleep
#import deepsleep

# Initialize LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN)
# create an OTAA authentication parameters
app_eui = binascii.unhexlify('70B3D57ED0007B4B')
app_key = binascii.unhexlify('7F038A1953C98DB8BD3C6E46F524D055')
#ds = DeepSleep()

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')
#pycom.heartbeat(False)
# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

s.setblocking(True)
s.bind(1)
print(bytes(struct.pack('>4s', "ping")))
s.send(bytes(struct.pack('>4s', "ping")))
s.setblocking(False)
data = s.recv(64)
if data:
    print("recvd data: {}".format(data))
    if data == b'\x01':
        pycom.rgbled(0x007f00)
    elif data == b'\x00':
        pycom.rgbled(0x000000)

print("going to sleep")
from machine import Pin
import machine

pinAlert = Pin('P13', mode=Pin.IN, pull= Pin.PULL_DOWN)
machine.pin_deepsleep_wakeup(['P13'], machine.WAKEUP_ANY_HIGH, True)
machine.deepsleep(600000)
#ds.enable_pullups('G30')
#ds.enable_wake_on_fall('G30')
#ds.go_to_sleep(60)
print("this should never happen")
