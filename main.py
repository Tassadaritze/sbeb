import random
import sys
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
CONST_INSTA_DUO_1_BTN_LOC = [810, 550]
CONST_INSTA_DUO_2_BTN_LOC = [1110, 550]
CONST_INSTA_TRIO_1_BTN_LOC = [656, 535]
CONST_INSTA_TRIO_2_BTN_LOC = [956, 535]
CONST_INSTA_TRIO_3_BTN_LOC = [1256, 535]
CONST_CONTINUE_BTN_LOC = [950, 1000]
CONST_CANCEL_BTN_LOC = [780, 730]
CONST_NUMBER_OF_EXPERT_MAP_SCREENS = 2
CONST_BONUS_TEMPLATE = cv.imread("bonus/pumpkin.png", cv.IMREAD_GRAYSCALE)  # thing to find


def get_map(page, x, y):
    index = 0
    expert_maps = ["sanctuary", "ravine", "flooded_valley", "infernal", "bloody_puddles", \
                    "workshop", "quad", "dark_castle", "muddy_puddles", "ouch"]
    top_row = y >= 120 and y <= 410
    bot_row = y >= 434 and y <= 723
    first_col = x >= 355 and x <= 717
    second_col = x >= 779 and x <= 1141
    third_col = x >= 1203 and x <= 1565

    if second_col:
        index += 1
    elif third_col:
        index += 2
    if bot_row:
        index += 3
    while page > 0:
        index += 6
        page -= 1

    print("Loading solution for " + expert_maps[index])

    return expert_maps[index]


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


def reveal_insta(insta_position):
    wa.SetCursorPos(insta_position)
    utils.click()
    sleep(0.3)
    utils.click()
    sleep(0.3)


def open_chest():
    wa.SetCursorPos(CONST_CHEST_BTN_LOC)
    utils.click()
    sleep(0.3)
    reveal_insta(CONST_INSTA_TRIO_1_BTN_LOC)
    reveal_insta(CONST_INSTA_DUO_1_BTN_LOC)
    reveal_insta(CONST_INSTA_TRIO_2_BTN_LOC)
    reveal_insta(CONST_INSTA_DUO_2_BTN_LOC)
    reveal_insta(CONST_INSTA_TRIO_3_BTN_LOC)
    wa.SetCursorPos(CONST_CONTINUE_BTN_LOC)
    utils.click()
    sleep(0.3)
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


def main():
    print("The program will take single screenshots of your first monitor for navigation purposes\n")

    # solutions.Monkey("dart", 834, 850)
    # solutions.Monkey("dart", 835, 925)

    print("Navigate to Bloons TD 6 main menu on monitor 1, then press Enter to continue")
    # print("Press Alt+1 to exit the program (hopefully)")
    # keyboard.add_hotkey("alt+1", lambda: sys.exit(0), suppress=True)
    # press enter after opening bloons on the main menu
    keyboard.wait("enter")

    # open_chest()
    # print(solutions.find_cash())
    # solutions.solve("sanctuary")
    # print(solutions.find_round())
    
    # keyboard.wait("enter")

    # input("Open BTD6 main menu on monitor 1, then press any key to continue")


    while True:
        nav_main_to_expert()

        match = False
        page = 0

        while not match:
            sleep(0.3)
            take_screenshot()
            # read in screenshot from file in grayscale
            menu_screenshot = cv.imread("monitor-1.png", cv.IMREAD_GRAYSCALE)
            cv.imwrite("gigatest.png", menu_screenshot)
            match = match_template(menu_screenshot, CONST_BONUS_TEMPLATE)
            if not match:
                utils.click()
                page = (page + 1) % CONST_NUMBER_OF_EXPERT_MAP_SCREENS
        else:
            utils.move_cursor(*match)
            utils.click()
            sleep(0.3)
            utils.move_cursor(632, 582)
            utils.click()
            sleep(0.3)
            utils.click()
            sleep(5)
            solutions.start_game()
            solutions.solve(get_map(page, *match))
            nav_victory_to_main()
            open_chest()

    # writes screen
    # cv.imwrite('res.png', screenshot)
    return


main()
