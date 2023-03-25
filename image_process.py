import subprocess
import cv2 as cv
import numpy as np
import pytesseract
from config import TESSERACTOR_PATH

pytesseract.pytesseract.tesseract_cmd = TESSERACTOR_PATH

def get_screenshot():
    with subprocess.Popen("adb shell screencap -p", stdout=subprocess.PIPE, shell=True) as proc: 
        screenshot_bytes = proc.stdout.read().replace(b'\r\n', b'\n')
        screenshot = cv.imdecode(np.frombuffer(screenshot_bytes, np.uint8), cv.IMREAD_COLOR)
        return screenshot

def fetch_screenshot_native_resolution():
    with subprocess.Popen("adb shell screencap -p", stdout=subprocess.PIPE, shell=True) as proc: 
        screenshot_bytes = proc.stdout.read().replace(b'\r\n', b'\n')
        screenshot = np.frombuffer(screenshot_bytes, np.uint8)
    with open('template_fetch.png', 'wb') as f:
        f.write(screenshot)

def ocr_rss_fetcher():
    img = get_screenshot()
    x, y, w, h = 987, 18, 300, 40
    crop_img = img[y:y+h, x:x+w]
    gray = cv.cvtColor(crop_img, cv.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    digit_substrings = text.replace(',', '').split()
    numbers = [int(substring) for substring in digit_substrings if substring.isdigit()]
    return numbers
          

def locate(media, threshold:float=0.90):
    screenshot = get_screenshot()
    template = cv.imread(f"media/{media}.png")
    result = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    if max_val >= threshold:
        return True
    else:
        return None

def locate_center(media, threshold:float=0.90):
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





