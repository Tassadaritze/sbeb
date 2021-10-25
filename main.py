import random
from time import sleep

import cv2 as cv
import keyboard
import win32api as wa
from mss import mss

import solutions
import utils

CONST_PLAY_BTN_LOC = [800, 950]
CONST_EXPERT_BTN_LOC = [1300, 1000]
CONST_NEXT_BTN_LOC = [960, 910]
CONST_HOME_BTN_LOC = [700, 850]
CONST_CHEST_BTN_LOC = [965, 395]
CONST_INSTA1_BTN_LOC = [810, 550]
CONST_INSTA2_BTN_LOC = [1110, 550]
CONST_CONTINUE_BTN_LOC = [950, 1000]
CONST_CANCEL_BTN_LOC = [780, 730]
CONST_BONUS_TEMPLATE = cv.imread("bonus.png", cv.IMREAD_GRAYSCALE)  # thing to find


# navigates from main menu to one of the expert map screens
def nav_main_to_expert():
    wa.SetCursorPos(CONST_PLAY_BTN_LOC)
    utils.click()
    slp = random.randrange(904, 1473)
    sleep(slp / 1000)
    wa.SetCursorPos(CONST_EXPERT_BTN_LOC)
    utils.click()
    sleep(0.3)


def nav_victory_to_main():
    wa.SetCursorPos(CONST_NEXT_BTN_LOC)
    utils.click()
    slp = random.randrange(904, 1473)
    sleep(slp / 1000)
    wa.SetCursorPos(CONST_HOME_BTN_LOC)
    utils.click()
    sleep(5)


def open_chest():
    wa.SetCursorPos(CONST_CHEST_BTN_LOC)
    utils.click()
    sleep(0.3)
    wa.SetCursorPos(CONST_INSTA1_BTN_LOC)
    utils.click()
    sleep(0.3)
    utils.click()
    sleep(0.3)
    wa.SetCursorPos(CONST_INSTA2_BTN_LOC)
    utils.click()
    sleep(0.3)
    utils.click()
    sleep(0.3)
    wa.SetCursorPos(CONST_CONTINUE_BTN_LOC)
    utils.click()
    sleep(0.3)
    utils.press('escape')
    sleep(0.3)
    wa.SetCursorPos(CONST_CANCEL_BTN_LOC)
    utils.click()
    sleep(0.3)


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


print("The program will take single screenshots of your first monitor for navigation purposes\n")

keyboard.wait('enter')

# open_chest()
solutions.find_cash()
# find_round()

# input("Open BTD6 main menu on monitor 1, then press any key to continue")

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

while False:
    # while not match:
    utils.click()
    sleep(0.3)
    take_screenshot()
    # read in screenshot from file in grayscale
    menu_screenshot = cv.imread("monitor-1.png", cv.IMREAD_GRAYSCALE)
    match = match_template(menu_screenshot, CONST_BONUS_TEMPLATE)
else:
    # wa.SetCursorPos(match)

    # hardcoded dark castle
    utils.click()
    sleep(0.3)
    # utils.move_cursor(950, 260) -- dark castle
    utils.move_cursor(532, 260)

    utils.click()
    sleep(0.3)
    utils.move_cursor(632, 582)
    utils.click()
    sleep(0.3)
    utils.click()
    sleep(5)
    solutions.start_game()
    # solutions.solve_dark_castle()
    solutions.solve_quad()
    nav_victory_to_main()
    # solve_infernal()
    open_chest()

# writes screen
# cv.imwrite('res.png', screenshot)
