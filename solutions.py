import logging as log
from time import sleep

import cv2 as cv
import numpy as np
import pytesseract

import utils
from config import hotkeys

CONST_UPG_TOP = "upg_top"
CONST_UPG_MID = "upg_mid"
CONST_UPG_BOT = "upg_bot"

placed_monkeys = {}


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
        utils.move_cursor(self.x, self.y)
        desired_key = hotkeys[self.type]
        utils.press(desired_key)
        utils.click()
    

    def select(self):
        utils.move_cursor(self.x, self.y)
        utils.click()


    def upgrade(self, path):
        if [CONST_UPG_TOP, CONST_UPG_MID, CONST_UPG_BOT].count(path) == 0:
            log.error("Tried to upgrade using invalid hotkey")
        else:
            self.select()
            utils.press(hotkeys[path])
            utils.press("esc")
    

    def set_targeting(self, desired_targeting):
        if self.targets.count(desired_targeting) == 0:
            log.error("Tried to set targeting using invalid hotkey")
        self.select()
        if self.type == "spac":
            return
        while self.target != self.targets.index(desired_targeting):
            utils.press(hotkeys["targ_next"])
            self.target = (self.target + 1) % 4
        utils.press("esc")


    def print_type(self):
        print("I am a " + self.type)


def start_game():
    utils.press(hotkeys["play_ff"])
    sleep(0.5)
    utils.press(hotkeys["play_ff"])


# Upgrade monkey located at given position on given path
def upgrade(path, position):
    if [CONST_UPG_TOP, CONST_UPG_MID, CONST_UPG_BOT].count(path) == 0:
        raise ValueError("Tried to upgrade using invalid hotkey")
    else:
        x = position[0]
        y = position[1]
        utils.move_cursor(x, y)
        utils.click()
        utils.press(hotkeys[path])
        utils.press("esc")


# returns current cash or -1 if OCR fails
def find_cash():
    utils.take_screenshot()
    screenshot = cv.imread("monitor-1.png")
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


# returns current round or -1 if OCR fails
def find_round():
    utils.take_screenshot()
    screenshot = cv.imread("monitor-1.png")
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


def place_monkey(monkey, x, y):
    utils.move_cursor(x, y)
    desired_key = hotkeys[monkey]
    utils.press(desired_key)
    utils.click()
    placed_monkeys.update({monkey: (x, y)})


# Sets targeting for tower located at position to Strong for normal towers or Smart for spactory
def set_targeting(position):
    x = position[0]
    y = position[1]
    utils.move_cursor(x, y)
    utils.click()
    utils.press(hotkeys["targ_prev"])
    utils.press("escape")


def solve_infernal():
    place_monkey("dart", 836, 387)


def solve_quad():
    dart1 = Monkey("dart", 834, 270)
    wait_for_cash(920)
    Monkey("hero", 1154, 322)
    wait_for_cash(170)
    sub1 = Monkey("sub", 960, 623)
    wait_for_cash(340)
    wiz1 = Monkey("wizard", 1267, 598)
    wait_for_cash(1020)
    wiz1.upgrade(CONST_UPG_MID)
    wiz1.upgrade(CONST_UPG_MID)
    wait_for_cash(230)
    wiz1.upgrade(CONST_UPG_BOT)
    wait_for_cash(255)
    wiz1.upgrade(CONST_UPG_BOT)
    wait_for_cash(700)
    spac1 = Monkey("spac", 398, 525)
    wait_for_cash(680)
    spac1.upgrade(CONST_UPG_TOP)
    wait_for_cash(510)
    spac1.upgrade(CONST_UPG_TOP)
    wait_for_cash(580)
    sniper1 = Monkey("sniper", 840, 714)
    sniper1.set_targeting("strong")
    sniper1.upgrade(CONST_UPG_TOP)
    wait_for_cash(680)
    sniper1.upgrade(CONST_UPG_BOT)
    sniper1.upgrade(CONST_UPG_BOT)
    wait_for_cash(1275)
    sniper1.upgrade(CONST_UPG_TOP)
    wait_for_cash(2975)
    sniper1.upgrade(CONST_UPG_BOT)
    wait_for_cash(3610)
    sniper1.upgrade(CONST_UPG_BOT)
    wait_for_round(39)
    wait_for_victory(25)


def solve_dark_castle():
    place_monkey("dart", 577, 491)
    wait_for_cash(920)
    place_monkey("hero", 910, 144)
    wait_for_cash(170)
    place_monkey("sub", 1083, 694)
    wait_for_cash(380)
    upgrade(CONST_UPG_BOT, placed_monkeys["sub"])
    wait_for_cash(850)
    upgrade(CONST_UPG_BOT, placed_monkeys["sub"])
    wait_for_cash(535)
    upgrade(CONST_UPG_TOP, placed_monkeys["sub"])
    upgrade(CONST_UPG_TOP, placed_monkeys["sub"])
    wait_for_cash(245)
    upgrade(CONST_UPG_BOT, placed_monkeys["dart"])
    upgrade(CONST_UPG_BOT, placed_monkeys["dart"])
    wait_for_cash(935)
    upgrade(CONST_UPG_BOT, placed_monkeys["sub"])
    wait_for_cash(2550)
    upgrade(CONST_UPG_BOT, placed_monkeys["sub"])
    wait_for_cash(530)
    upgrade(CONST_UPG_BOT, placed_monkeys["dart"])
    wait_for_cash(470)
    place_monkey("alch", 924, 666)
    wait_for_cash(1700)
    upgrade(CONST_UPG_TOP, placed_monkeys["alch"])
    upgrade(CONST_UPG_TOP, placed_monkeys["alch"])
    upgrade(CONST_UPG_TOP, placed_monkeys["alch"])
    wait_for_cash(615)
    upgrade(CONST_UPG_MID, placed_monkeys["alch"])
    upgrade(CONST_UPG_MID, placed_monkeys["alch"])
    wait_for_cash(2550)
    upgrade(CONST_UPG_TOP, placed_monkeys["alch"])

    # just in case
    wait_for_cash(6000)
    upgrade(CONST_UPG_BOT, placed_monkeys["sub"])
    upgrade(CONST_UPG_TOP, placed_monkeys["alch"])
    wait_for_round(39)
    wait_for_victory(27)
