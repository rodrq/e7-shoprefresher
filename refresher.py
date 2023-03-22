import subprocess
import cv2 as cv
import numpy as np
import time
import pytesseract
import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

def adb_command(text:str):
    return subprocess.run([word for word in text.split()])

def get_screenshot():
    with subprocess.Popen("adb shell screencap -p", stdout=subprocess.PIPE, shell=True) as proc: 
        screenshot_bytes = proc.stdout.read().replace(b'\r\n', b'\n')
        screenshot = cv.imdecode(np.frombuffer(screenshot_bytes, np.uint8), cv.IMREAD_COLOR)
        return screenshot
    
def get_screenshot_native_resolution():
    with subprocess.Popen("adb shell screencap -p", stdout=subprocess.PIPE, shell=True) as proc: 
        screenshot_bytes = proc.stdout.read().replace(b'\r\n', b'\n')
        screenshot = np.frombuffer(screenshot_bytes, np.uint8)
    with open('template_fetch.png', 'wb') as f:
        f.write(screenshot)

def locate(media, threshold:float=0.90):
    screenshot = get_screenshot()
    template = cv.imread(f"media/{media}.png")
    result = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    w, h = template.shape[:-1]
    center_w = int(max_loc[0] + w/2)
    center_h = int(max_loc[1] + h/2)
    if max_val >= threshold:
        return f"{center_w} {center_h}"
    else:
        return None


def buy_summon(summon):
    coords = locate(summon)
    if coords != None:
        coords = coords.split(' ')
        coords = f"{int(coords[0])+700} {int(coords[1])+40}"
        while not locate('confirm_buy'):
            adb_command(f'adb shell input tap {coords}')
            time.sleep(0.5)
        while locate('confirm_buy'):
            adb_command(f'adb shell input tap 900 630')
        print(f"Bought {summon}")
        time.sleep(1)
        return True
    else:
        return None


    


def dispatch_completed_checker():
    if locate('dispatch_completed'):
        print('Dispatch mission completed')
        adb_command('adb shell input tap 1070 720')
        print('Waiting for second dispatch mission')
        time.sleep(8)
        adb_command('adb shell input tap 1070 720')

def connection_error_checker():
    if locate('connection_error'):
        print('Closing connection error pop-up. ')
        adb_command('adb shell input tap 800 800')
        time.sleep(3)



def refresher():
    print('Shop refreshing')
    while not locate('confirm_refresh'):
            adb_command('adb shell input tap 290 826')
            time.sleep(0.4)

    while locate('confirm_refresh'):
            adb_command('adb shell input tap 950 550')
            time.sleep(0.4)



def ocr_rss_fetcher():
    img = get_screenshot()
    x, y, w, h = 987, 18, 300, 40
    crop_img = img[y:y+h, x:x+w]
    gray = cv.cvtColor(crop_img, cv.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    digit_substrings = text.replace(',', '').split()
    # Convert each substring to an integer
    numbers = [int(substring) for substring in digit_substrings if substring.isdigit()]
    return numbers
          

def main():
    gold, skystones = ocr_rss_fetcher()
    covenants_bought = 0
    mystics_bought= 0
    print(f"Gold = {gold}. \nSkystones = {skystones}")
    while True:
        connection_error_checker()
        dispatch_completed_checker()
        swiped = False
        for n in range(2):
            if buy_summon('mystics'):
                gold -= 280000
                mystics_bought += 1
            if buy_summon('covenant'):
                gold -= 184000
                covenants_bought += 1
            if swiped==False:
                adb_command('adb shell input touchscreen swipe 1250 580 1250 200')
                swiped=True
        if gold < 280000 or skystones < 1800:
            print('Script terminated because gold or skystones limit surpassed')
            break
        refresher()
        skystones -= 3
        print(f"Current gold: {gold} \nCurrent skystones: {skystones} \nCovenants bought: {covenants_bought} \nMystics bought: {mystics_bought}")


while True:
    main()
    






