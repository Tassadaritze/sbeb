import random as random
from time import sleep

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import win32api as wa
import win32con as wc
from mss import mss

CONST_PLAY_BTN_LOC = [800, 950]
CONST_EXPERT_BTN_LOC = [1300, 1000]
CONST_BONUS_TEMPLATE = cv.imread("bonus.png", cv.IMREAD_GRAYSCALE)  # thing to find


# clicks like a human (with some delay)
def click():
    wa.mouse_event(2, 0, 0)          # hold down lmb
    slp = random.randrange(97, 205)
    sleep(slp / 1000)
    wa.mouse_event(4, 0, 0)          # release lmb


# navigates from main menu to one of the expert map screens
def nav_main_to_expert():
    wa.SetCursorPos(CONST_PLAY_BTN_LOC)
    click()
    slp = random.randrange(904, 1473)
    print(slp)
    sleep(slp / 1000)
    wa.SetCursorPos(CONST_EXPERT_BTN_LOC)
    click()
    sleep(0.3)

def move_cursor(x,y):
    wa.SetCursorPos([x,y])
    
def place_monkey(monkey):
  m = 81
  # monkey_list = [["dart", Q], ["ben", U]]
  wa.keybd_event(m, m, 0, 0)
  slp = random.randrange(97, 205)
  sleep(slp / 1000)
  wa.keybd_event(m, m, wc.KEYEVENTF_KEYUP, 0)
  click()

# returns the top left coordinates of tmpl inside of img
def match_template(img, tmpl):
  res = cv.matchTemplate(img, tmpl, cv.TM_CCOEFF_NORMED)
  min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
  if max_val > 0.3:
    return max_loc
  else:
    return False


# saves screenshot to "monitor-1.png"
def take_screenshot():
  with mss() as sct:
    sct.shot()


def solve_quad():
  move_cursor(835,271)
  place_monkey("dart")
    

print("The program will take single screenshots of your first monitor for navigation purposes\n")

# input("Open BTD6 main menu on monitor 1, then press any key to continue")
nav_main_to_expert()

match = False

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

while match == False:
  click()
  sleep(0.3)  
  take_screenshot()
  # read in screenshot from file in grayscale
  screenshot = cv.imread("monitor-1.png", cv.IMREAD_GRAYSCALE)
  match = match_template(screenshot, CONST_BONUS_TEMPLATE)  
else:
  wa.SetCursorPos(match)
  click()
  sleep(0.3)
  move_cursor(632,582)
  click()
  sleep(0.3)
  click()
  sleep(5)
  solve_quad()

# writes screen
cv.imwrite('res.png', screenshot)
#opens image for debugging lole
plt.imshow(screenshot), plt.show()
