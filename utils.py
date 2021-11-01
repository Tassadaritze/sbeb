import random
from time import sleep

import cv2 as cv
import keyboard
import win32api as wa
from mss import mss


def move_cursor(x, y):
    wa.SetCursorPos([x, y])


# clicks like a human (with some delay)
def click():
    wa.mouse_event(2, 0, 0)  # hold down lmb
    slp = random.randrange(97, 205)
    sleep(slp / 1000)
    wa.mouse_event(4, 0, 0)  # release lmb
    sleep(0.2)


def press(button):
    keyboard.press_and_release(button)
    sleep(0.2)


# saves screenshot to "monitor1.png" and returns a greyscaled image
def take_screenshot(location="screenshots/monitor1.png"):
    with mss() as sct:
        sct.shot(output=location)
    return cv.imread(location, cv.IMREAD_GRAYSCALE)


# returns the top left coordinates of tmpl inside of img
def match_template(img, tmpl):
    w, h = tmpl.shape[::-1]
    res = cv.matchTemplate(img, tmpl, cv.TM_CCOEFF_NORMED)
    print(res)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    print(max_val)
    if max_val > 0.85:
        return [max_loc[0] + w//2, max_loc[1] + h//2]
    else:
        return False
