# Import what is necessary to create a thread
import _thread
from time import sleep

# Increment index used to scan each point from vector sensors_data
def inc(index, vector):
    if index < len(vector)-1:
        return index+1
    else:
        return 0

# Define your thread's behaviour, here it's a loop sending sensors data every 5 seconds
def send_env_data():
    idx = 0
    sensors_data = [0, -0.2, -0.5, -0.7, -0.8, -0.9, -0.9, -0.9, -0.8, -0.6, -0.4, -0.2, 0, 0.3, 0.5, 0.7, 0.8, 0.9, 0.9, 0.9, 0.8, 0.6, 0.4, 0.1]

    while True:
        # send one element from array `sensors_data` as signal 1
        pybytes.send_signal(1, sensors_data[idx])
        idx = inc(idx, sensors_data)
        sleep(5)

# Start your thread
_thread.start_new_thread(send_env_data, ())
