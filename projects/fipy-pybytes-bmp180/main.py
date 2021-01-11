# Import what is necessary to create a thread
import _thread
from time import sleep
#import machine
from machine import Pin, I2C
from bmp085 import BMP180
import pycom

pycom.heartbeat(False)
i2c = I2C()
bmp = BMP180(i2c)
bmp.oversample = 2
bmp.sealevel = 101325


# Define your thread's behaviour, here it's a loop sending sensors data every 5 seconds
def send_env_data():
    while True:
        temp = bmp.temperature
        press = bmp.pressure
        altitude = bmp.altitude
        print("temp: {} pres: {} alt: {}".format(temp, press, altitude))
        pybytes.send_signal(1, temp)
        pybytes.send_signal(2, press)
        pybytes.send_signal(3, altitude)
        sleep(60)

pybytes.set_config('lte', { "band": 20, "apn": "ep.inetd.gdsp", "reset": True})
pybytes.set_config('network_preferences', ["lte"])
print(pybytes.print_config())
import pycom
pycom.nvs_set('pybytes_debug', 1)
# Start your thread
_thread.start_new_thread(send_env_data, ())
#pybytes.send_signal(2, 25.6)
#sleep(0.5)
# powerdown 15 mins
#machine.deepsleep(900000)
