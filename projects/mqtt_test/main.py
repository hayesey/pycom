from mqtt import MQTTClient
import machine
import time
from network import WLAN
from machine import Pin

p_in = Pin('P23', mode=Pin.IN, pull=Pin.PULL_UP)

def sub_cb(topic, msg):
    print("MQTTmsg: "+msg)

wlan = WLAN(mode=WLAN.STA)
wlan.connect("technical", auth=(WLAN.WPA2, "#technical"), timeout=5000)

while not wlan.isconnected():
    machine.idle()
print("Connected to wifi, IP is:"+wlan.ifconfig()[0]+"\n")

client = MQTTClient("lopy", "192.168.2.155", user="", password="", port=1883)

client.set_callback(sub_cb)
client.connect()
client.subscribe(topic="test/button")

pin_pressed = False

def send_message(mqttmsg):
    if not client:
        client.connect()
    client.publish(topic="test/button", msg=mqttmsg)

while True:
    if p_in():
        # button not pressed
        if pin_pressed:
            time.sleep(0.1)
            send_message("Button-Up")
        pin_pressed = False
    elif not p_in():
        # button is pressed
        if not pin_pressed:
            time.sleep(0.1)
            send_message("Button-Down")
        pin_pressed = True
