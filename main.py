from image_process import *
from config import LIMIT_SKYSTONES, LIMIT_GOLD

### OCR ROTO #################!!!!!!!!!!!!!!!!!!!!!!

adb_connect()
#TEMPORAL
gold = int(input('Current gold: '))
#TEMPORAL
skystones = int(input('Current skystones: '))

skystones_spent = 0
gold_spent = 0
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
        refresher()
        skystones -= 3
        skystones_spent += 3
        print(f"Current gold: {gold} out of {limit_gold} \nCurrent skystones: {skystones} out of {limit_skystones} \nCovenants bought: {covenants_bought} \nMystics bought: {mystics_bought}")

