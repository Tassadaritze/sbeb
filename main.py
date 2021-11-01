import os
import random
import sys
from time import sleep

import cv2 as cv
import keyboard

import solutions
from utils import click, match_template, move_cursor, press, take_screenshot

PLAY_BTN_LOC = (800, 950)
EXPERT_BTN_LOC = (1300, 1000)
NEXT_BTN_LOC = (960, 910)
HOME_BTN_LOC = (700, 850)
CHEST_BTN_LOC = (965, 395)
CONTINUE_BTN_LOC = (950, 1000)
CANCEL_BTN_LOC = (780, 730)
NUMBER_OF_EXPERT_MAP_SCREENS = 2
PLAY_BUTTON_TEMPLATE = cv.imread("templates/play_button.png", cv.IMREAD_GRAYSCALE)
REVEAL_INSTA_TEMPLATE = cv.imread("templates/secret_insta.png", cv.IMREAD_GRAYSCALE)
BONUS_TEMPLATE = cv.imread("templates/pumpkin.png", cv.IMREAD_GRAYSCALE)  # image of current bonus event marker


def get_map(page, x, y):
    index = 0
    EXPERT_MAPS = ["sanctuary", "ravine", "flooded_valley", "infernal", "bloody_puddles", \
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

    print("Loading solution for " + EXPERT_MAPS[index])

    return EXPERT_MAPS[index]


# navigates from main menu to one of the expert map screens
def nav_main_to_expert():
    move_cursor(*PLAY_BTN_LOC)
    click()
    slp = random.randrange(904, 1473)
    sleep(slp / 1000)
    move_cursor(*EXPERT_BTN_LOC)
    click()
    sleep(0.3)


def nav_victory_to_main():
    move_cursor(*NEXT_BTN_LOC)
    click()
    slp = random.randrange(904, 1473)
    sleep(slp / 1000)
    move_cursor(*HOME_BTN_LOC)
    click()
    sleep(5)


def reveal_insta(insta_position):
    move_cursor(*insta_position)
    click()
    sleep(0.3)
    click()
    sleep(0.3)


def open_chest():
    move_cursor(*CHEST_BTN_LOC)
    click()
    sleep(0.6)
    match = match_template(take_screenshot(), REVEAL_INSTA_TEMPLATE)
    while match:
        move_cursor(*match)
        click()
        sleep(0.3)
        click()
        sleep(0.3)
        match = match_template(take_screenshot(), REVEAL_INSTA_TEMPLATE)
    move_cursor(*CONTINUE_BTN_LOC)
    click()
    sleep(0.3)
    click()
    sleep(0.3)
    press('escape')
    sleep(0.3)
    move_cursor(*CANCEL_BTN_LOC)
    click()
    sleep(0.3)


def main():
    print("The program will take and store single screenshots of your first monitor for navigation purposes\n")
    
    print("Navigate to Bloons TD 6 main menu on monitor 1, then press Enter to continue")
    # print("Press Alt+1 to exit the program (hopefully)")
    # keyboard.add_hotkey("alt+1", lambda: sys.exit(0), suppress=True)

    # press enter after opening bloons on the main menu
    keyboard.wait("enter")

    screenshot_path = "screenshots"
    if not os.path.exists(screenshot_path):
        os.makedirs(screenshot_path)

    while True:
        nav_main_to_expert()

        match = False
        page = 0

        while not match:
            sleep(0.3)
            match = match_template(take_screenshot(), BONUS_TEMPLATE)
            if not match:
                click()
                page = (page + 1) % NUMBER_OF_EXPERT_MAP_SCREENS
        else:
            move_cursor(*match)
            click()
            sleep(0.3)
            move_cursor(632, 582)
            click()
            sleep(0.3)
            click()
            solutions.solve(get_map(page, *match))
            nav_victory_to_main()
            if not match_template(take_screenshot(), PLAY_BUTTON_TEMPLATE):
                open_chest()
    return


main()
