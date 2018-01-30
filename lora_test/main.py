from network import LoRa
import socket
import time
import binascii
import struct
import math
import pycom
from machine import Pin, ADC, Timer, UART
from nmea import NmeaParser

gps_pps = Pin('P22', mode = Pin.IN)
gps_enable = Pin('P8', mode=Pin.OUT)
gps_enable(False)
#gps_uart = UART(2, 9600)
#gps_uart.init(9600, bits=8, parity=None, stop=1)
gps_uart = UART(2, baudrate=9600, bits=8, parity=None, stop=1, pins=('P10', 'P11'))
gps_uart.write('abs')
gps_enable(True)

# Initialize LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN)
pin_pressed = False
p_in = Pin('P23', mode=Pin.IN, pull=Pin.PULL_UP)

resistance = 33 #33k thermistor and resistor
beta = 4090 # from thermistor datasheet 1187032 farnell
adc = ADC(0)
therm_pin = adc.channel(attn=3, pin='P16')
temperature = 0.0

# create an OTAA authentication parameters
app_eui = binascii.unhexlify('70B3D57ED0007B4B')
app_key = binascii.unhexlify('7F038A1953C98DB8BD3C6E46F524D055')

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')
pycom.heartbeat(False)
# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

def send_data(temperature, lon, lat):
    s.setblocking(True)
    s.bind(1)
    #s.send(bytes([1, 0, pin_data, 2, 103]) + struct.pack('>h', int(temperature * 10)))
    s.send(bytes(struct.pack('>hii', int(temperature * 100), int(lat * 1000000), int(lon * 1000000))))
    s.setblocking(False)
    data = s.recv(64)
    if data:
        print("recvd data: {}".format(data))
        if data == b'\x01':
            pycom.rgbled(0x007f00)
        elif data == b'\x00':
            pycom.rgbled(0x000000)

def readTemp():
    return (beta / (math.log(((4095.0 * resistance / therm_pin()) - resistance) / resistance) + (beta / 298.0)) - 273.0) + 5

def timerCallback(timer):
    nParser = NmeaParser()
    lon = 0.0
    lat = 0.0
    while gps_uart.any():
        line = gps_uart.readline()
        #if line.startswith("b'$GPGGA"):
        if nParser.update(line):
            lat = nParser.latitude
            lon = nParser.longitude
            print("lon: {} lat: {}".format(lon, lat))

    # read temp pin and convert to celcius, with a +5 bodge as it seems more correct!
    temperature = readTemp()
    print("temp is: {}".format(temperature))
    send_data(temperature, lon, lat)

timer = Timer.Alarm(timerCallback, 60, periodic=True)

while True:
    if p_in():
        # button not pressed
        if pin_pressed:
            time.sleep(0.1)
            print("button released")
            pin_pressed = False
            send_data()
    elif not p_in():
        # button is pressed
        if not pin_pressed:
            time.sleep(0.1)
            print("button pressed")
            pin_pressed = True
            send_data()
