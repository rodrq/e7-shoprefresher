from adb import *
from image_process import *
from config import LIMIT_SKYSTONES, LIMIT_GOLD
import time

def refresher():
    print('Shop refreshing')
    while not locate('confirm_refresh'):
            adb_command('adb shell input tap 290 826')
            time.sleep(0.1)

    while locate('confirm_refresh'):
            adb_command('adb shell input tap 950 550')
            time.sleep(0.1)

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

def find_buy_summon(summon):
    coords = locate_center(summon)
    if coords != None:
        coords = coords.split(' ')
        coords = f"{int(coords[0])+700} {int(coords[1])+40}"
        while not locate('confirm_buy'):
            adb_command(f'adb shell input tap {coords}')
            time.sleep(0.1)
        while locate('confirm_buy'):
            adb_command(f'adb shell input tap 900 630')
            time.sleep(0.1)
        print(f"Bought {summon}")
        return True
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


def main():
    adb_connect()
    gold, skystones = ocr_rss_fetcher()
    covenants_bought = 0
    mystics_bought= 0
    limit_skystones = LIMIT_SKYSTONES
    limit_gold = LIMIT_GOLD
    print(f"Gold = {gold}. \nSkystones = {skystones}")
    if in_secretshop():
        while True:
            already_bought_m= False
            already_bought_c=False
            connection_error_checker()
            dispatch_completed_checker()
            if gold < limit_gold or skystones < limit_skystones:
                print('Script terminated because gold or skystones limit surpassed')
                break
            swiped = False
            for n in range(2):
                if not already_bought_m:
                    if find_buy_summon('mystics'):
                        gold -= 280000
                        mystics_bought += 1
                        already_bought_m = True
                if not already_bought_c:
                    if find_buy_summon('covenant'):
                        gold -= 184000
                        covenants_bought += 1
                        already_bought_c = True
                if not swiped:
                    adb_command('adb shell input touchscreen swipe 1250 580 1250 200')
                    swiped=True
            if gold < limit_gold or skystones < limit_skystones:
                print('Script terminated because gold or skystones limit surpassed')
                break
            refresher()
            skystones -= 3
            print(f"Current gold: {gold} out of {limit_gold} \nCurrent skystones: {skystones} out of {limit_skystones} \nCovenants bought: {covenants_bought} \nMystics bought: {mystics_bought}")