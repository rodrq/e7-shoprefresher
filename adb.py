"""
Some functions to make the use of adb outside a cmd less of a headache.
"""

import subprocess
from time import sleep

def adb_command(text:str):
    return subprocess.run([word for word in text.split()])

def adb_connect():
    adb_command('adb start-server')
    adb_command('adb devices')

def adb_tap(x, y, taps = 1):
    for n in range(taps):
        adb_command(f"adb shell input tap {x} {y}")
        sleep(0.05)
        
