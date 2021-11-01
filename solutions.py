import logging as log
from time import sleep

import cv2 as cv
import numpy as np

from config import hotkeys
from utils import click, match_template, move_cursor, press, take_screenshot

UPG_TOP = "upg_top"
UPG_MID = "upg_mid"
UPG_BOT = "upg_bot"
NEXT_BUTTON_TEMPLATE = cv.imread("templates/next_button.png", cv.IMREAD_GRAYSCALE)
MONKEY_COSTS = {
    "dart": {"base": 170, UPG_TOP: (120, 185, 255, 1530, 12750), UPG_MID: (85, 160, 340, 6800, 38250), UPG_BOT: (75, 170, 530, 1700, 21250)},
    "boomer": "w",
    "bomb": "e",
    "tack": "r",
    "ice": "t",
    "glue": "z",
    "sniper": {"base": 285, UPG_TOP: (295, 1275, 2550, 3250, 28900), UPG_MID: (255, 380, 2720, 6120, 11050), UPG_BOT: (340, 340, 2975, 3610, 11900)},
    "sub": {"base": 275, UPG_TOP: (110, 425, 425, 2125, 27200), UPG_MID: (380, 255, 1190, 11050, 27200), UPG_BOT: (380, 850, 935, 2550, 21250)},
    "bucc": "c",
    "ace": {"base": 645, UPG_TOP: (550, 550, 850, 2550, 30600), UPG_MID: (170, 295, 765, 11900, 26775), UPG_BOT: (425, 255, 1870, 20400, 76500)},
    "heli": "b",
    "mortar": "n",
    "dartling": "m",
    "wizard": {"base": 340, UPG_TOP: (100, 510, 1105, 9265, 27200), UPG_MID: (255, 765, 2550, 3400, 45900), UPG_BOT: (230, 255, 1445, 2380, 20400)},
    "super": "s",
    "ninja": "d",
    "alch": {"base": 470, UPG_TOP: (210, 295, 1060, 2550, 51000), UPG_MID: (210, 405, 2550, 3825, 38250), UPG_BOT: (550, 380, 850, 2335, 34000)},
    "druid": "g",
    "farm": "h",
    "spac": {"base": 850, UPG_TOP: (680, 510, 1955, 6575, 127500), UPG_MID: (510, 680, 2125, 4250, 34000), UPG_BOT: (125, 340, 1190, 2975, 25500)},
    "village": "k",
    "engi": "l",
    "hero": {"base": 920},
}

class Monkey:
    def __init__(self, type, x, y):
        self.type = type
        self.x = x
        self.y = y
        self.upgrades = {UPG_TOP: 0, UPG_MID: 0, UPG_BOT: 0}
        self.target = 0
        self.targets = ["first", "last", "close", "strong"]
        self.costs = MONKEY_COSTS[type]
        self.place()


    def place(self):
        wait_for_cash(self.costs["base"])
        move_cursor(self.x, self.y)
        desired_key = hotkeys[self.type]
        press(desired_key)
        click()
        self.identify()
    

    def select(self):
        move_cursor(self.x, self.y)
        click()


    def upgrade(self, path):
        if [UPG_TOP, UPG_MID, UPG_BOT].count(path) == 0:
            log.error("Tried to upgrade using invalid hotkey")
        else:
            wait_for_cash(self.get_upgrade_costs(path))
            self.select()
            press(hotkeys[path])
            press("esc")
            self.upgrades[path] += 1
            self.identify()
    

    def get_upgrade_costs(self, path):
        next_upgrade = self.upgrades[path]
        return self.costs[path][next_upgrade]


    def set_targeting(self, desired_targeting):
        if self.targets.count(desired_targeting) == 0:
            log.error("Tried to set targeting using invalid hotkey")
        self.select()
        if self.type == "spac":
            return
        while self.target != self.targets.index(desired_targeting):
            press(hotkeys["targ_next"])
            self.target = (self.target + 1) % 4
        press("esc")


    def has_left_menu(self):
        self.x >= 835


    def identify(self):
        print(f"I am a {self.upgrades[UPG_TOP]}/{self.upgrades[UPG_MID]}/{self.upgrades[UPG_BOT]} {self.type}")


def start_game():
    wait_for_cash(650)
    press(hotkeys["play_ff"])
    sleep(0.3)
    press(hotkeys["play_ff"])


# Upgrade monkey located at given position on given path
def upgrade(path, position):
    if [UPG_TOP, UPG_MID, UPG_BOT].count(path) == 0:
        raise ValueError("Tried to upgrade using invalid hotkey")
    else:
        x = position[0]
        y = position[1]
        move_cursor(x, y)
        click()
        press(hotkeys[path])
        press("esc")


def find_number_on_screen(x_start, x_end, y_start, y_end):
    thresh = cv.adaptiveThreshold(take_screenshot(), 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 7, 2)
    number_crop = thresh[y_start:y_end, x_start:x_end]
    digits = {}
    for i in range(10):
        digit = cv.imread(f"numbers/{i}.png", cv.IMREAD_GRAYSCALE)
        w, h = digit.shape[::-1]                                      # Dimensions of input template, only 2 arguments because image is grayscale
        match = cv.matchTemplate(number_crop, digit, cv.TM_CCOEFF_NORMED)
        threshold = 0.75
        loc = np.where(match >= threshold)                            # NumPy is a fuck
        last_x = False
        loc[1].sort()
        true_loc = loc[1].tolist()                                    # Have to convert NumPy array to a normal fucking list
        for x in loc[1]:                                              # Goes through list of x-coordinates of matched points
            if isinstance(last_x, np.int64) and x - last_x < w // 2:  # Checks if last_x is a NumPy int64 and if it's too close to the next element
                true_loc.pop(true_loc.index(last_x))                  # Removes last_x from list if it's too close to the next element
            last_x = x                                                # Sets last_x up for next iteration and we go agane
        digits.update(dict.fromkeys(true_loc, i))
    sorted_digits = sorted(digits.items())
    sorted_digits = [str(x[1]) for x in sorted_digits]
    try:
        found_number = int("".join(sorted_digits))
        return found_number
    except ValueError:
        print("Could not recognise value")
        return -1


# returns current cash or -1 if template matching fails
def find_cash():
    return find_number_on_screen(345, 530, 20, 65)


def wait_for_cash(amount):
    sleep(1)
    current_cash = find_cash()
    while current_cash < amount:
        print(f"Current cash: {current_cash} < {amount}")
        sleep(3)
        current_cash = find_cash()
    else:
        print(f"Current cash: {current_cash} >= {amount}")
        return


# returns current round or -1 if template matching fails
def find_round():
    return find_number_on_screen(1420, 1486, 28, 70)


def wait_for_round(number):
    sleep(1)
    current_round = find_round()
    while current_round < number:
        print(f"Current round: {current_round} < {number}")
        sleep(10)
        current_round = find_round()
    else:
        print(f"Current round: {current_round} >= {number}")
        return


def wait_for_victory():
    print("res:")
    match = match_template(take_screenshot(), NEXT_BUTTON_TEMPLATE)
    if not match:
        sleep(3)
        wait_for_victory()
  

# Sets targeting for tower located at position to Strong for normal towers or Smart for spactory
def set_targeting(position):
    x = position[0]
    y = position[1]
    move_cursor(x, y)
    click()
    press(hotkeys["targ_prev"])
    press("escape")


def solve(map):
    start_game()
    eval("solve_" + map + "()")


# hardcoded solution, because of moving parts of the map
def solve_sanctuary():
    Monkey("hero", 833, 150)
    Monkey("sniper", 256, 964)
    click()
    press(hotkeys["targ_prev"])
    wait_for_cash(340)
    press(hotkeys[UPG_BOT])
    wait_for_cash(340)
    press(hotkeys[UPG_BOT])
    wait_for_cash(295)
    press(hotkeys[UPG_TOP])
    wait_for_cash(2975)
    press(hotkeys[UPG_BOT])
    wait_for_cash(3610)
    press(hotkeys[UPG_BOT])
    wait_for_cash(1275)
    press(hotkeys[UPG_TOP])
    wait_for_cash(11900)
    press(hotkeys[UPG_BOT])
    press("escape")
    wait_for_round(39)
    wait_for_victory()


def solve_ravine():
    dart1 = Monkey("dart", 1353, 266)
    dart2 = Monkey("dart", 704, 103)
    sniper1 = Monkey("sniper", 549, 148)
    sniper1.set_targeting("strong")
    sniper2 = Monkey("sniper", 1283, 284)
    Monkey("hero", 696, 212)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sniper2.upgrade(UPG_BOT)
    sniper2.upgrade(UPG_BOT)
    sniper2.upgrade(UPG_MID)
    sniper2.upgrade(UPG_MID)
    sniper1.upgrade(UPG_TOP)
    sniper2.upgrade(UPG_BOT)
    sniper2.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory()


def solve_flooded_valley():
    sub1 = Monkey("sub", 973, 197)
    Monkey("hero", 745, 429)
    sub2 = Monkey("sub", 1011, 841)
    sub1.upgrade(UPG_MID)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_MID)
    sub2.upgrade(UPG_TOP)
    sub2.upgrade(UPG_TOP)
    sub2.upgrade(UPG_BOT)
    sub2.upgrade(UPG_BOT)
    sub2.upgrade(UPG_BOT)
    sub3 = Monkey("sub", 1027, 911)
    sub3.upgrade(UPG_MID)
    sub3.upgrade(UPG_MID)
    sub3.upgrade(UPG_BOT)
    sniper1 = Monkey("sniper", 270, 736)
    sniper1.upgrade(UPG_MID)
    sniper1.upgrade(UPG_MID)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sub2.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory()


def solve_infernal():
    dart1 = Monkey("dart", 834, 387)
    sub1 = Monkey("sub", 487, 789)
    sniper1 = Monkey("sniper", 1568, 599)
    sniper1.set_targeting("strong")
    Monkey("hero", 122, 643)
    sniper1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_TOP)
    dart1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sniper2 = Monkey("sniper", 1578, 532)
    sniper2.upgrade(UPG_MID)
    sniper2.upgrade(UPG_MID)
    sniper2.upgrade(UPG_BOT)
    sniper2.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    sniper2.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory()


def solve_bloody_puddles():
    dart1 = Monkey("dart", 393, 304)
    dart3 = Monkey("dart", 1255, 833)
    Monkey("hero", 836, 434)
    sub1 = Monkey("sub", 1217, 175)
    sniper1 = Monkey("sniper", 712, 62)
    sniper1.set_targeting("strong")
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_TOP)
    dart2 = Monkey("dart", 939, 354)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    dart2.upgrade(UPG_BOT)
    dart2.upgrade(UPG_BOT)
    dart3.upgrade(UPG_BOT)
    dart3.upgrade(UPG_BOT)
    dart4 = Monkey("dart", 357, 806)
    dart4.upgrade(UPG_BOT)
    dart4.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_TOP)
    sniper1 = Monkey("sniper", 771, 1042)
    sniper1.upgrade(UPG_MID)
    sniper1.upgrade(UPG_MID)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory()


def solve_workshop():
    dart1 = Monkey("dart", 920, 502)
    Monkey("hero", 1214, 267)
    sniper1 = Monkey("sniper", 1020, 500)
    sniper1.set_targeting("strong")
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_TOP)
    sniper2 = Monkey("sniper", 953, 496)
    sniper2.upgrade(UPG_BOT)
    sniper2.upgrade(UPG_BOT)
    sniper2.upgrade(UPG_MID)
    sniper2.upgrade(UPG_MID)
    sniper2.upgrade(UPG_BOT)
    sniper2.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_TOP)
    wait_for_round(39)
    wait_for_victory()


def solve_quad():
    sniper1 = Monkey("sniper", 840, 714)
    sniper1.set_targeting("strong")
    sub1 = Monkey("sub", 960, 623)
    dart1 = Monkey("dart", 834, 270)
    Monkey("hero", 1154, 322)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    sniper2 = Monkey("sniper", 715, 703)
    sniper2.set_targeting("strong")
    sniper2.upgrade(UPG_TOP)
    sniper2.upgrade(UPG_MID)
    sniper2.upgrade(UPG_MID)
    sniper2.upgrade(UPG_MID)
    sniper2.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory()


def solve_dark_castle():
    dart1 = Monkey("dart", 577, 491)
    Monkey("hero", 910, 144)
    sub1 = Monkey("sub", 1083, 694)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    sniper1 = Monkey("sniper", 1452, 358)
    sniper1.set_targeting("strong")
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory()


def solve_muddy_puddles():
    dart1 = Monkey("dart", 467, 296)
    Monkey("hero", 980, 690)
    sub1 = Monkey("sub", 1203, 450)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_BOT)
    sniper1 = Monkey("sniper", 1229, 43)
    sniper1.set_targeting("strong")
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    dart2 = Monkey("dart", 1114, 195)
    dart1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    dart2.upgrade(UPG_BOT)
    dart2.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory()


def solve_ouch():
    dart1 = Monkey("dart", 666, 507)
    Monkey("hero", 1133, 322)
    sub1 = Monkey("sub", 978, 612)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_MID)
    dart1.upgrade(UPG_MID)
    sniper1 = Monkey("sniper", 1023, 324)
    sniper1.set_targeting("strong")
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory()


# DEBUG automatic cash detection with gathered images from find_cash().
# 1. turn on image saving in find_cash() =>
# 2. run program for a while
# 3. rename images where the name doesnt match the number in debug folder to "name"-"number_in_image", e.g. 421-4271 if 7 wasn't detected.
# 4. run debug_cash()
# 5. finetune images in numbers folder and/or threshold in find_cash_debug
"""
import os
import re

def debug_cash():
    still_correct = [0, 0]
    improved = [0, 0]
    path = 'debug'
    dir = sorted(os.listdir(path), key=len)
    for name in dir :
        crop = cv.imread(f"debug/{name}", cv.IMREAD_GRAYSCALE)
        if str.__contains__(name, '-'):
            found_cash = find_cash_debug(crop)
            if found_cash > 0:
                correct_val = re.sub(r'.*-', '', name)[:-4]
                print(f"{correct_val} == {found_cash}")
                if correct_val == str(found_cash):
                    improved[0] += 1
                    improved[1] += 1
                else:
                    improved[1] += 1
            else:
                improved[1] += 1
        elif True:
            found_cash = find_cash_debug(crop)
            if found_cash > 0:    
                # print(f"{n[:-4]} == {found_cash}")
                if name[:-4] == str(found_cash):
                    still_correct[0] += 1
                    still_correct[1] += 1
                else:
                    print(f"{name[:-4]} != {found_cash}")
                    still_correct[1] += 1
            else:
                still_correct[1] += 1
    print(f"Still correct: {still_correct[0]}/{still_correct[1]}")
    print(f"Now also correct: {improved[0]}/{improved[1]}")
    

def find_cash_debug(picture):
    digits = {}
    for i in range(10):
        digit = cv.imread(f"numbers/{i}.png", cv.IMREAD_GRAYSCALE)
        w, h = digit.shape[::-1]                                      # Dimensions of input template, only 2 arguments because image is grayscale
        match = cv.matchTemplate(picture, digit, cv.TM_CCOEFF_NORMED)
        threshold = 0.75
        loc = np.where(match >= threshold)                            # NumPy is a fuck
        last_x = False
        loc[1].sort()
        true_loc = loc[1].tolist()                                    # Have to convert NumPy array to a normal fucking list
        for x in loc[1]:                                              # Goes through list of x-coordinates of matched points
            if isinstance(last_x, np.int64) and x - last_x < w // 2:  # Checks if last_x is a NumPy int64 and if it's too close to the next element
                true_loc.pop(true_loc.index(last_x))                  # Removes last_x from list if it's too close to the next element
            last_x = x                                                # Sets last_x up for next iteration and we go agane
        digits.update(dict.fromkeys(true_loc, i))
    sorted_digits = sorted(digits.items())
    sorted_digits = [str(x[1]) for x in sorted_digits]
    try:
        found_cash = int("".join(sorted_digits))
        # cv.imwrite(f"debug/{found_cash}.png", picture)
        return found_cash
    except ValueError:
        print("Could not recognise cash value")
        return -1
"""