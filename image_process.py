import subprocess
import cv2 as cv
import numpy as np
import pytesseract
from config import TESSERACT_PATH
from adb import *
from time import sleep

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def get_screenshot():
    #Grabs binary with 'adb screencap', loads it into numpy and converts to grayscale and 2D array for OpenCV use.
    with subprocess.Popen("adb exec-out screencap -p", stdout=subprocess.PIPE, shell=True) as proc: 
        screenshot_binary = np.frombuffer(proc.stdout.read(), np.uint8)
        screenshot = cv.imdecode(screenshot_binary, cv.IMREAD_GRAYSCALE)
        return screenshot


def fetch_screenshot_native_resolution():
    with subprocess.Popen("adb exec-out screencap -p", stdout=subprocess.PIPE, shell=True) as proc: 
        screenshot_bytes = proc.stdout.read()
        screenshot = np.frombuffer(screenshot_bytes, np.uint8)
    with open('template_fetch.png', 'wb') as f:
        f.write(screenshot)


def ocr_rss_fetcher():
    img = get_screenshot()
    x, y, w, h = 987, 18, 300, 40
    crop_img = img[y:y+h, x:x+w]
    text = pytesseract.image_to_string(crop_img)
    digit_substrings = text.replace(',', '').split()
    numbers = [int(substring) for substring in digit_substrings if substring.isdigit()]
    return numbers
          

def locate(media, threshold:float=0.90, region = (0, 0, 1600, 900)):
    """Main function of the whole script.
    Compares a template with screenshot and if it matches more than 90% (by default) returns True.
    Mostly used as a logic gate to avoid getting the bot stuck when a "Confirm" input or something doesn't register.
    Region parameter added inspired by py_autogui to make the script faster.    
    """
    screenshot = get_screenshot()
    template = cv.imread(f"media/{media}.png", cv.IMREAD_GRAYSCALE)
    x, y, w, h = region
    screenshot = screenshot[y:y+h, x:x+w]
    result = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    if max_val >= threshold:
        return True
    else:
        return None

def locate_center(media, threshold:float=0.90, region = (0, 0, 1600, 900)):
    """
    Same logic as 'locate()' but some math to return the center of the object 
    so we can send a tap input to it.
    """
    screenshot = get_screenshot()
    template = cv.imread(f"media/{media}.png", cv.IMREAD_GRAYSCALE)
    xr, yr, wr, hr = region
    screenshot = screenshot[yr:yr+hr, xr:xr+wr]
    result = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    if max_val >= threshold:
        found_w = int(max_loc[0] + xr)
        found_h = int(max_loc[1] + yr)
        h, w = template.shape
        center_w = int(found_w + w/2)
        center_h = int(found_h + h/2)
        return f"{center_w} {center_h}"
    else:
        return None

def in_secretshop():
    print('Checking if in secret shop')
    if locate('secretshop_title'):
        print('Checked')
        return True
    else:
        print('Please open secret shop. Closing script')
        return False

def refresher():
    print('Shop refreshing')
    while not locate('confirm_refresh'):
            adb_tap(290, 826)
            sleep(0.25)
    while locate('confirm_refresh'):
            adb_tap(950, 550)
            sleep(0.25)

def dispatch_completed_checker():
    if locate('dispatch_completed'):
        print('Dispatch mission completed')
        adb_tap(1070, 720)
        print('Waiting for second dispatch mission')
        sleep(8)
        adb_tap(1070, 720)


def connection_error_checker():
    if locate('connection_error'):
        print('Closing connection error pop-up. ')
        adb_tap(800, 800)
        sleep(3)

def find_buy_summon(summon):
    coords = locate_center(summon, region=(680, 80, 150, 900-80))
    if coords:
        coords = coords.split(' ')
        while not locate('confirm_buy'):
            #adb_command(f'adb shell input tap {coords}')
            adb_tap(int(coords[0])+700, int(coords[1]) + 40)
            sleep(0.15)
        while locate('confirm_buy'):
            adb_tap(900, 630)
            sleep(0.15)
        print(f"Bought {summon}")
        return True
    else:
        return None

