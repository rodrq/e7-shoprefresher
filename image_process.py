import subprocess
import cv2 as cv
import numpy as np
from config import LIMIT_SKYSTONES, LIMIT_GOLD
from adb import *
from time import sleep


def get_screenshot():
    #Grabs binary with 'adb screencap', loads it into numpy and converts to grayscale and 2D array for OpenCV use.
    with subprocess.Popen("adb exec-out screencap -p", stdout=subprocess.PIPE, shell=True) as proc: 
        result = proc.stdout.read()
        screenshot_binary = np.frombuffer(result, np.uint8)
        screenshot = cv.imdecode(screenshot_binary, cv.IMREAD_GRAYSCALE)
        return screenshot


def fetch_screenshot_native_resolution():
    # Function used to get templates with the same quality and resolution as get_screenshot(), since my emulator window is resized.
    with subprocess.Popen("adb exec-out screencap -p", stdout=subprocess.PIPE, shell=True) as proc: 
        screenshot_bytes = proc.stdout.read()
        screenshot = np.frombuffer(screenshot_bytes, np.uint8)
    with open('template_fetch.png', 'wb') as f:
        f.write(screenshot)

          

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
    """
    Many while loops since sometimes inputs don't register in the front-end and bugs the whole thing out.
    """
    print('Shop refreshing')
    while not locate('confirm_refresh'):
            adb_tap(290, 826, taps=2)
            sleep(0.25)
    while locate('confirm_refresh'):
            adb_tap(950, 550, taps=2)
            sleep(0.32)

def dispatch_completed_checker():
    if locate('dispatch_completed'):
        print('Dispatch mission completed')
        adb_tap(1070, 720, taps=3)
        print('Waiting for second dispatch mission')
        sleep(8)
        adb_tap(1070, 720, taps=3)

        

def find_buy_summon(summon):
    """
    Finds and buys the summon. Searches the row where items appear to speed up a bit the script with (region= x, x, x, x). 
    """
    coords = locate_center(summon, region=(680, 80, 150, 820))
    if coords:
        coords = coords.split(' ')
        while not locate('confirm_buy'):
            #+700 +60 is the offset where the "buy" button appears in comparison to the template. 
            adb_tap(int(coords[0])+700, int(coords[1]) + 60, taps= 2)
            sleep(0.15)
        while locate('confirm_buy'):
            adb_tap(900, 630, taps=2)
            sleep(0.15)
        print(f"Bought {summon}")
        return True
    else:
        return None



def connection_error_checker():
    """This should be a separate thread that checks constantly and sets a flag 
    to stop the script but found a messy logic workaround that worked so all good.
    """
    error_located = False
    while locate('connection_error') or locate('ras_connection_error'):
            error_located=True
            print('Connection error located. Trying to close and/or waiting.')
            adb_tap(800, 800, taps=2)
            sleep(10)
    return error_located


### PROGRAM LOGIC ###
def main():
    adb_connect()
    #On both these inputs, I should check that just integers are entered. But it works fine and already bored of this project.
    gold = int(input('Current gold: '))
    skystones = int(input('Current skystones: '))
    skystones_spent = 0
    gold_spent = 0
    covenants_bought = 0
    mystics_bought= 0
    limit_skystones = LIMIT_SKYSTONES
    limit_gold = LIMIT_GOLD
    error_found = False
    while True:
        already_bought_m= False
        already_bought_c=False
        if gold < limit_gold or skystones < limit_skystones:
            print('Script terminated because gold or skystones limit surpassed')
            break
        swiped = False
        # Needs to be checked twice since the last item only shows after scrolling down the shop menu. Swiped = False to True is to avoid a second scroll-down.
        for n in range(2):
            if not already_bought_m:
                if find_buy_summon('mystics'):
                    gold -= 280000
                    gold_spent += 280000
                    mystics_bought += 1
                    already_bought_m = True
            if not already_bought_c:
                if find_buy_summon('covenant'):
                    gold -= 184000
                    gold_spent += 184000
                    covenants_bought += 1
                    already_bought_c = True
            if not swiped:
                adb_command('adb shell input touchscreen swipe 1250 580 1250 200')
                swiped=True
        if gold < limit_gold or skystones < limit_skystones:
            print('Script terminated because gold or skystones limit surpassed')
            print(f'STATS:\nCovenants bought: {covenants_bought}\nMystics bought: {mystics_bought}\nSkystones spent: {skystones_spent}\nGold spent: {gold_spent}')
            break
        """
        This is the messy logic workaround I found. Since the script only bugs when stuck at waiting for a certain template and
        connection errors could make these never appear. I check for them before the intensive image processing task of refreshing
        the shop. 
        If the connection error appeared just before confirming the refresh, the script would refresh twice. So I added that simple
        boolean variable.
        Just messy coding. 
        """
        if connection_error_checker() == True:
            error_found = True
        if not error_found:
            refresher()
        error_found = False
        skystones -= 3
        skystones_spent += 3
        print(f"Current gold: {gold} out of {limit_gold} \nCurrent skystones: {skystones} out of {limit_skystones} \nCovenants bought: {covenants_bought} \nMystics bought: {mystics_bought}")
        sleep(2)