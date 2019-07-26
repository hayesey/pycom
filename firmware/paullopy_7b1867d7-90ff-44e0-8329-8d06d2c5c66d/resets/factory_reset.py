'''Run this file to overwrite main.py/boot.py, useful if a device’s filesystem gets corrupted'''
import os
os.mkfs('/flash')
