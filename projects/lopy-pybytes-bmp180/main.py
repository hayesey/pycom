#
# this example assumes the default connection for the I2C Obviously
# at P9 = sda and P10 = scl
#
import _thread
from time import sleep
from machine import Pin, I2C
from bmp085 import BMP180

i2c = I2C()
bmp = BMP180(i2c)
bmp.oversample = 2
bmp.sealevel = 101325

def send_env_data():
    while True:
        temp = bmp.temperature
        press = bmp.pressure
        altitude = bmp.altitude
        print("temp: {} pres: {} alt: {}".format(temp, press, altitude))
        pybytes.send_signal(1, temp)
        pybytes.send_signal(2, press)
        pybytes.send_signal(3, altitude)
        sleep(600)

_thread.start_new_thread(send_env_data, ())
