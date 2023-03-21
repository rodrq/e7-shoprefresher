import subprocess
import time
import cv2 as cv
import numpy as np

def adb_command(text:str):
    return subprocess.run([word for word in text.split()])

def get_screenshot():
    with subprocess.Popen("adb shell screencap -p", stdout=subprocess.PIPE, shell=True) as proc: 
        image_bytes = proc.stdout.read().replace(b'\r\n', b'\n')
        image = cv.imdecode(np.frombuffer(image_bytes, np.uint8), cv.IMREAD_COLOR)
        return image

def locate(media, threshold:float=0.75):
    screenshot = get_screenshot()
    template = cv.imread(f"media/{media}.png")
    result = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    w, h = template.shape[:-1]
    center = (int(max_loc[0] + w/2), int(max_loc[1] + h/2))
    if max_val >= threshold:
        return center
    else:
        print('Image not found')
        return None



def buy(media):
    get_coords = locate(media)
    if get_coords:
        pass
    else:
        pass

