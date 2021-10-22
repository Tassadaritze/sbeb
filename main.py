import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from mss import mss
import win32api as wa
from time import sleep
import random as random
import sys

CONST_PLAY_BTN_LOC = [800, 950]
CONST_EXPERT_BTN_LOC = [1300, 1000]
CONST_BONUS_TEMPLATE = cv.imread("bonus.png", cv.IMREAD_GRAYSCALE)  # thing to find


def rand_click():
    wa.mouse_event(2, 0, 0)          # hold down lmb
    slp = random.randrange(97, 205)
    print(slp)
    sleep(slp / 1000)
    wa.mouse_event(4, 0, 0)          # release lmb

# navigates from main menu to one of the expert map screens
def main_to_expert():
    wa.SetCursorPos(CONST_PLAY_BTN_LOC)
    rand_click()
    slp = random.randrange(904, 1473)
    print(slp)
    sleep(slp / 1000)
    wa.SetCursorPos(CONST_EXPERT_BTN_LOC)
    rand_click()
    sleep(0.3)

# returns the top left coordinates of tmpl inside of img
def match_template(img, tmpl):
    res = cv.matchTemplate(img, tmpl, cv.TM_CCOEFF_NORMED)
    loc = cv.minMaxLoc(res)  # tuple of matching coordinates
    print(loc)
    return loc

# saves screenshot to "monitor-1.png"
def take_screenshot():
    with mss() as sct:
      sct.shot()


print("The program will take single screenshots of your first monitor for navigation purposes\n")

# input("Open BTD6 main menu on monitor 1, then press any key to continue")
main_to_expert()
take_screenshot()

# read in screenshot from file in grayscale
screenshot = cv.imread("monitor-1.png", cv.IMREAD_GRAYSCALE)

# match = location tuple
match = match_template(screenshot, CONST_BONUS_TEMPLATE)
""" for i in match:
    end = 0
    end = end + len(match[i])
    while end == 0:
        rand_click()
        sleep(0.5)
        match += match_template(scrn, CONST_BONUS_TEMPLATE)
        print(match) """

""" for pt in zip(*match[::-1]):
    wa.SetCursorPos(pt)
    cv.rectangle(scrn, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    rand_click() """

# writes screen
cv.imwrite('res.png', screenshot)
#opens image for debugging lole
plt.imshow(screenshot), plt.show()
