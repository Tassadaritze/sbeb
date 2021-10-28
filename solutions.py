import logging as log
from time import sleep

import cv2 as cv
import numpy as np

from config import hotkeys
from utils import click, move_cursor, press, take_screenshot

UPG_TOP = "upg_top"
UPG_MID = "upg_mid"
UPG_BOT = "upg_bot"


class Monkey:
    def __init__(self, type, x, y):
        self.type = type
        self.x = x
        self.y = y
        self.upgrades = [0, 0, 0]
        self.target = 0
        self.targets = ["first", "last", "close", "strong"]
        self.place()


    def place(self):
        move_cursor(self.x, self.y)
        desired_key = hotkeys[self.type]
        press(desired_key)
        click()
    

    def select(self):
        move_cursor(self.x, self.y)
        click()


    def upgrade(self, path):
        if [UPG_TOP, UPG_MID, UPG_BOT].count(path) == 0:
            log.error("Tried to upgrade using invalid hotkey")
        else:
            self.select()
            press(hotkeys[path])
            press("esc")
    

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


    def print_type(self):
        print("I am a " + self.type)


def start_game():
    press(hotkeys["play_ff"])
    sleep(0.5)
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


# returns current cash or -1 if OCR fails (deprecated in favour of a non-ML approach)
"""
def find_cash():
    take_screenshot()
    screenshot = cv.imread("screenshots/monitor1.png")
    # screenshot = cv.medianBlur(screenshot, 5)
    gray = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 220, 255, cv.THRESH_BINARY_INV)[1]
    #,+ cv.THRESH_OTSU)[1]
    cash_crop = thresh[20:65, 345:500]
    kernel = np.ones((3,3),np.uint8)
    cash_crop = cv.erode(cash_crop ,kernel,iterations = 2)
    cv.imwrite('cash.png', cash_crop)

    custom_oem_psm_config = r'--oem 3 --psm 13'
    tesseract_out = pytesseract.image_to_string(cash_crop,
                                                config=custom_oem_psm_config)  # Tesseract does its best to recognise something
    found_cash_list = [s for s in list(tesseract_out) if s.isdigit()]  # Find digits in what was recognised
    print(tesseract_out)
    try:
        found_cash = int("".join(found_cash_list))
        return found_cash
    except ValueError:
        print("Could not recognise cash value")
        return -1
"""


# returns current cash or -1 if template matching fails
def find_cash():
    take_screenshot()
    screenshot = cv.imread("screenshots/monitor1.png", cv.IMREAD_GRAYSCALE)
    thresh = cv.adaptiveThreshold(screenshot, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 7, 2)
    cash_crop = thresh[20:65, 345:530]
    digits = {}
    for i in range(10):
        digit = cv.imread("numbers/" + str(i) + ".png", cv.IMREAD_GRAYSCALE)
        w, h = digit.shape[::-1]                                      # Dimensions of input template, only 2 arguments because image is grayscale
        match = cv.matchTemplate(cash_crop, digit, cv.TM_CCOEFF_NORMED)
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
        # cv.imwrite("debug/" + str(found_cash) + ".png", cash_crop)
        return found_cash
    except ValueError:
        print("Could not recognise cash value")
        return -1


def wait_for_cash(amount):
    sleep(1)
    current_cash = find_cash()
    while current_cash < amount:
        print("current: " + str(current_cash) + " < " + str(amount))
        sleep(3)
        current_cash = find_cash()
    else:
        print(str(current_cash) + " > " + str(amount))
        return


# returns current round or -1 if OCR fails (deprecated in favour of a non-ML approach)
"""
def find_round():
    take_screenshot()
    screenshot = cv.imread("screenshots/monitor1.png")
    gray = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    round_crop = thresh[30:65, 1430:1485]  # crop
    cv.imwrite('round.png', round_crop)
    custom_oem_psm_config = r'--oem 3 --psm 13'
    tesseract_out = pytesseract.image_to_string(round_crop,
                                                config=custom_oem_psm_config)  # Tesseract does its best to recognise something
    print(tesseract_out)
    found_round_list = [s for s in list(tesseract_out) if s.isdigit()]  # Find digits in what was recognised
    try:
        found_round = int("".join(found_round_list))
        return found_round
    except ValueError:
        print("Could not recognise round value")
        return -1
"""


# returns current round or -1 if template matching fails
def find_round():
    take_screenshot()
    screenshot = cv.imread("screenshots/monitor1.png", cv.IMREAD_GRAYSCALE)
    thresh = cv.adaptiveThreshold(screenshot, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 7, 2)
    round_crop = thresh[28:70, 1420:1486]
    digits = {}
    for i in range(10):
        digit = cv.imread("numbers/" + str(i) + ".png", cv.IMREAD_GRAYSCALE)
        w, h = digit.shape[::-1]                                      # Dimensions of input template, only 2 arguments because image is grayscale
        match = cv.matchTemplate(round_crop, digit, cv.TM_CCOEFF_NORMED)
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
        found_round = int("".join(sorted_digits))
        return found_round
    except ValueError:
        print("Could not recognise round value")
        return -1



def wait_for_round(number):
    sleep(1)
    current_round = find_round()
    while current_round < number:
        print("current round: " + str(current_round) + " < " + str(number))
        sleep(3)
        current_round = find_round()
    else:
        print("current round: " + str(current_round) + " >= " + str(number))
        return


def wait_for_victory(seconds):
    sleep(seconds)


# Sets targeting for tower located at position to Strong for normal towers or Smart for spactory
def set_targeting(position):
    x = position[0]
    y = position[1]
    move_cursor(x, y)
    click()
    press(hotkeys["targ_prev"])
    press("escape")


def solve(map):
    eval("solve_" + map + "()")


# hardcoded solution, because of moving parts of the map
def solve_sanctuary():
    wait_for_cash(920)
    Monkey("hero", 833, 150)
    wait_for_cash(185)
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
    wait_for_victory(20)


def solve_ravine():
    dart1 = Monkey("dart", 1353, 266)
    wait_for_cash(920)
    Monkey("hero", 703, 109)
    wait_for_cash(420)
    ace1 = Monkey("ace", 534, 829)
    wait_for_cash(425)
    ace1.upgrade(UPG_BOT)
    wait_for_cash(255)
    ace1.upgrade(UPG_BOT)
    wait_for_cash(1870)
    ace1.upgrade(UPG_BOT)
    wait_for_cash(470)
    alch1 = Monkey("alch", 359, 814)
    wait_for_cash(505)
    alch1.upgrade(UPG_TOP)
    alch1.upgrade(UPG_TOP)
    wait_for_cash(1060)
    alch1.upgrade(UPG_TOP)
    wait_for_cash(615)
    alch1.upgrade(UPG_MID)
    alch1.upgrade(UPG_MID)
    wait_for_cash(1100)
    ace1.upgrade(UPG_TOP)
    ace1.upgrade(UPG_TOP)
    wait_for_cash(2550)
    alch1.upgrade(UPG_TOP)
    wait_for_cash(1600)
    sniper1 = Monkey("sniper", 123, 887)
    sniper1.upgrade(UPG_MID)
    sniper1.upgrade(UPG_MID)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory(20)


def solve_flooded_valley():
    wait_for_cash(920)
    Monkey("hero", 745, 429)
    wait_for_cash(170)
    sub1 = Monkey("sub", 973, 197)
    wait_for_cash(380)
    sub1.upgrade(UPG_MID)
    wait_for_cash(380)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(850)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(935)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(255)
    sub1.upgrade(UPG_MID)
    wait_for_cash(260)
    sub2 = Monkey("sub", 1011, 841)
    wait_for_cash(535)
    sub2.upgrade(UPG_TOP)
    sub2.upgrade(UPG_TOP)
    wait_for_cash(1230)
    sub2.upgrade(UPG_BOT)
    sub2.upgrade(UPG_BOT)
    wait_for_cash(3485)
    sub2.upgrade(UPG_BOT)
    sub2.upgrade(UPG_BOT)
    wait_for_cash(2550)
    sub1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory(20)


def solve_infernal():
    dart1 = Monkey("dart", 834, 387)
    wait_for_cash(920)
    Monkey("hero", 122, 643)
    wait_for_cash(75)
    dart1.upgrade(UPG_BOT)
    wait_for_cash(170)
    sub1 = Monkey("sub", 487, 789)
    wait_for_cash(535)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_TOP)
    wait_for_cash(170)
    dart1.upgrade(UPG_BOT)
    wait_for_cash(1230)
    sub1.upgrade(UPG_BOT)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(285)
    sniper1 = Monkey("sniper", 1568, 599)
    sniper1.set_targeting("strong")
    wait_for_cash(975)
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    wait_for_cash(935)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(2550)
    sub1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory(20)


def solve_bloody_puddles():
    dart1 = Monkey("dart", 393, 304)
    wait_for_cash(920)
    Monkey("hero", 836, 434)
    wait_for_cash(170)
    sub1 = Monkey("sub", 1217, 175)
    wait_for_cash(535)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_TOP)
    wait_for_cash(170)
    dart2 = Monkey("dart", 939, 354)
    wait_for_cash(170)
    dart3 = Monkey("dart", 1255, 833)
    wait_for_cash(380)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(850)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(1260)
    sniper1 = Monkey("sniper", 712, 62)
    sniper1.set_targeting("strong")
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    wait_for_cash(735)
    dart1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    dart2.upgrade(UPG_BOT)
    dart2.upgrade(UPG_BOT)
    dart3.upgrade(UPG_BOT)
    dart3.upgrade(UPG_BOT)
    wait_for_cash(415)
    dart4 = Monkey("dart", 357, 806)
    dart4.upgrade(UPG_BOT)
    dart4.upgrade(UPG_BOT)
    wait_for_cash(935)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(2550)
    sub1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory(20)


def solve_workshop():
    dart1 = Monkey("dart", 920, 502)
    wait_for_cash(920)
    Monkey("hero", 1214, 267)
    wait_for_cash(340)
    wiz1 = Monkey("wizard", 1020, 499)
    wait_for_cash(255)
    wiz1.upgrade(UPG_MID)
    wait_for_cash(765)
    wiz1.upgrade(UPG_MID)
    wait_for_cash(230)
    wiz1.upgrade(UPG_BOT)
    wait_for_cash(255)
    wiz1.upgrade(UPG_BOT)
    wait_for_cash(700)
    spac1 = Monkey("spac", 1016, 409)
    wait_for_cash(680)
    spac1.upgrade(UPG_TOP)
    wait_for_cash(465)
    spac1.upgrade(UPG_BOT)
    spac1.upgrade(UPG_BOT)
    wait_for_cash(1190)
    spac1.upgrade(UPG_BOT)
    wait_for_cash(2975)
    spac1.upgrade(UPG_BOT)
    wait_for_cash(510)
    spac1.upgrade(UPG_TOP)
    wait_for_cash(850)
    spac2 = Monkey("spac", 1549, 677)
    wait_for_cash(680)
    spac2.upgrade(UPG_TOP)
    wait_for_cash(465)
    spac2.upgrade(UPG_BOT)
    spac2.upgrade(UPG_BOT)
    wait_for_cash(1190)
    spac2.upgrade(UPG_BOT)
    wait_for_cash(2975)
    spac2.upgrade(UPG_BOT)
    wait_for_cash(510)
    spac2.upgrade(UPG_TOP)
    wait_for_round(39)
    wait_for_victory(20)


def solve_quad():
    dart1 = Monkey("dart", 834, 270)
    wait_for_cash(920)
    Monkey("hero", 1154, 322)
    wait_for_cash(170)
    sub1 = Monkey("sub", 960, 623)
    wait_for_cash(340)
    wiz1 = Monkey("wizard", 1267, 598)
    wait_for_cash(1020)
    wiz1.upgrade(UPG_MID)
    wiz1.upgrade(UPG_MID)
    wait_for_cash(230)
    wiz1.upgrade(UPG_BOT)
    wait_for_cash(255)
    wiz1.upgrade(UPG_BOT)
    wait_for_cash(700)
    spac1 = Monkey("spac", 398, 525)
    wait_for_cash(680)
    spac1.upgrade(UPG_TOP)
    wait_for_cash(510)
    spac1.upgrade(UPG_TOP)
    wait_for_cash(580)
    sniper1 = Monkey("sniper", 840, 714)
    sniper1.set_targeting("strong")
    sniper1.upgrade(UPG_TOP)
    wait_for_cash(680)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    wait_for_cash(1275)
    sniper1.upgrade(UPG_TOP)
    wait_for_cash(2975)
    sniper1.upgrade(UPG_BOT)
    wait_for_cash(3610)
    sniper1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory(20)


def solve_dark_castle():
    dart1 = Monkey("dart", 577, 491)
    wait_for_cash(920)
    Monkey("hero", 910, 144)
    wait_for_cash(170)
    sub1 = Monkey("sub", 1083, 694)
    wait_for_cash(380)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(850)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(535)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_TOP)
    wait_for_cash(245)
    dart1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    wait_for_cash(935)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(2550)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(530)
    dart1.upgrade(UPG_BOT)
    wait_for_cash(470)
    alch1 = Monkey("alch", 924, 666)
    wait_for_cash(1700)
    alch1.upgrade(UPG_TOP)
    alch1.upgrade(UPG_TOP)
    alch1.upgrade(UPG_TOP)
    wait_for_cash(615)
    alch1.upgrade(UPG_MID)
    alch1.upgrade(UPG_MID)
    wait_for_cash(2550)
    alch1.upgrade(UPG_TOP)
    wait_for_round(39)
    wait_for_victory(20)


def solve_muddy_puddles():
    dart1 = Monkey("dart", 467, 296)
    wait_for_cash(920)
    Monkey("hero", 980, 690)
    wait_for_cash(170)
    sub1 = Monkey("sub", 1203, 450)
    wait_for_cash(535)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_TOP)
    wait_for_cash(380)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(850)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(285)
    sniper1 = Monkey("sniper", 1229, 43)
    sniper1.set_targeting("strong")
    wait_for_cash(975)
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    wait_for_cash(660)
    dart2 = Monkey("dart", 1138, 775)
    dart1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    dart2.upgrade(UPG_BOT)
    dart2.upgrade(UPG_BOT)
    wait_for_cash(935)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(2550)
    sub1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory(20)


def solve_ouch():
    dart1 = Monkey("dart", 666, 507)
    wait_for_cash(920)
    Monkey("hero", 1133, 322)
    wait_for_cash(170)
    sub1 = Monkey("sub", 978, 612)
    wait_for_cash(535)
    sub1.upgrade(UPG_TOP)
    sub1.upgrade(UPG_TOP)
    wait_for_cash(380)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(850)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(245)
    dart1.upgrade(UPG_BOT)
    dart1.upgrade(UPG_BOT)
    wait_for_cash(530)
    dart1.upgrade(UPG_BOT)
    wait_for_cash(245)
    dart1.upgrade(UPG_MID)
    dart1.upgrade(UPG_MID)
    wait_for_cash(285)
    sniper1 = Monkey("sniper", 1023, 324)
    sniper1.set_targeting("strong")
    wait_for_cash(975)
    sniper1.upgrade(UPG_TOP)
    sniper1.upgrade(UPG_BOT)
    sniper1.upgrade(UPG_BOT)
    wait_for_cash(935)
    sub1.upgrade(UPG_BOT)
    wait_for_cash(2550)
    sub1.upgrade(UPG_BOT)
    wait_for_round(39)
    wait_for_victory(20)
