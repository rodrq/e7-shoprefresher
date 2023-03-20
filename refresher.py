import subprocess
import time
import cv2 as cv
import numpy as np

def adb_command(text:str):
    return subprocess.run([word for word in text.split()])

def get_screenshot():
    adb_command('adb shell screencap -p /sdcard/screenshot.png')
    adb_command('adb pull /sdcard/screenshot.png screenshot.png')

def locate(media, threshold:float):
    screenshot = cv.imread('screenshot.png')
    template = cv.imread(f"media/{media}.png")
    result = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    print(max_val)
    if max_val >= threshold:
        return True
    elif max_val < threshold:
        return False


def buy():
    if locate('mystics', 0.8):
        pass

