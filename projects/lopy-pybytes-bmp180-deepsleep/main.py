#
# this example assumes the default connection for the I2C Obviously
# at P9 = sda and P10 = scl
#
from deepsleep import DeepSleep
import deepsleep
#from machine import Pin, I2C
#from bmp085 import BMP180
import pycom

pycom.heartbeat(False)

ds = DeepSleep()
#i2c = I2C()
#bmp = BMP180(i2c)
#bmp.oversample = 2
#bmp.sealevel = 101325

#temp = bmp.temperature
#press = bmp.pressure
#altitude = bmp.altitude
#print("temp: {} pres: {} alt: {}".format(temp, press, altitude))
#pybytes.send_signal(1, temp)
#pybytes.send_signal(2, press)
#pybytes.send_signal(3, altitude)

pybytes.send_signal(4, "ping")
print("going to sleep")
ds.enable_pullups('G30')
ds.enable_wake_on_fall('G30')
ds.go_to_sleep(60)
print("this should never happen")
