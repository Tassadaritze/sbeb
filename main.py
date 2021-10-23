import random as random
from time import sleep

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import win32api as wa
import keyboard
import pytesseract
from mss import mss

CONST_PLAY_BTN_LOC = [800, 950]
CONST_EXPERT_BTN_LOC = [1300, 1000]
CONST_BONUS_TEMPLATE = cv.imread("bonus.png", cv.IMREAD_GRAYSCALE)  # thing to find

placed_monkeys = {}


# clicks like a human (with some delay)
def click():
    wa.mouse_event(2, 0, 0)  # hold down lmb
    slp = random.randrange(97, 205)
    sleep(slp / 1000)
    wa.mouse_event(4, 0, 0)  # release lmb


def press(button):
    keyboard.press_and_release(button)
    sleep(0.01)


def upgrade_top(position):
    x = position[0]
    y = position[1]
    move_cursor(x, y)
    click()
    sleep(0.2)
    press(',')


def upgrade_mid(position):
    x = position[0]
    y = position[1]
    move_cursor(x, y)
    click()
    sleep(0.2)
    press('.')


def upgrade_bot(position):
    x = position[0]
    y = position[1]
    move_cursor(x, y)
    click()
    sleep(0.2)
    press('/')
    

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


def move_cursor(x, y):
    wa.SetCursorPos([x, y])


def place_monkey(monkey, x, y):
    move_cursor(x, y)
    monkey_list = {"dart": 'q', "hero": 'u', "sub": 'x', "sniper": 'z', "spac": 'j', "wizard": 'a'}
    desired_key = monkey_list[monkey]
    press(desired_key)
    click()
    placed_monkeys.update({monkey: (x, y)})


def start_game():
    press('space')
    sleep(0.5)
    press('space')


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
    return


def solve_dark_castle():
    place_monkey("dart", 577, 491)
    sleep(12)
    place_monkey("hero", 910, 144)
    sleep(10)
    place_monkey("sub", 1083, 694)
    click()
    print(placed_monkeys.items())
    sleep(15)
    upgrade_bot(placed_monkeys["sub"])
    

print("The program will take single screenshots of your first monitor for navigation purposes\n")

# input("Open BTD6 main menu on monitor 1, then press any key to continue")

img_cv = cv.imread(r'./test.png')

# By default OpenCV stores images in BGR format and since pytesseract assumes RGB format,
# we need to convert from BGR to RGB format/mode:
img_rgb = cv.cvtColor(img_cv, cv.COLOR_BGR2RGB)
print(pytesseract.image_to_string(img_rgb))

# press enter after opening bloons on the main menu
keyboard.wait('enter')
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

while not match:
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
    move_cursor(632, 582)
    click()
    sleep(0.3)
    click()
    sleep(5)
    start_game()
    solve_dark_castle()

# writes screen
# cv.imwrite('res.png', screenshot)
# opens image for debugging lole
# plt.imshow(screenshot), plt.show()
