import random as random
from time import sleep

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import win32api as wa
import keyboard
import pytesseract
import imutils
from mss import mss

CONST_PLAY_BTN_LOC = [800, 950]
CONST_EXPERT_BTN_LOC = [1300, 1000]
CONST_NEXT_BTN_LOC = [960, 910]
CONST_HOME_BTN_LOC = [700, 850]
CONST_CHEST_BTN_LOC = [940, 530]
CONST_INSTA1_BTN_LOC = [810, 550]
CONST_INSTA2_BTN_LOC = [1110, 550]
CONST_CONTINUE_BTN_LOC = [950, 1000]
CONST_CANCEL_BTN_LOC = [780, 730]
CONST_BONUS_TEMPLATE = cv.imread("bonus.png", cv.IMREAD_GRAYSCALE)  # thing to find

placed_monkeys = {}


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


def upgrade_top(position):
    x = position[0]
    y = position[1]
    move_cursor(x, y)
    click()
    press(',')
    press('escape')


def upgrade_mid(position):
    x = position[0]
    y = position[1]
    move_cursor(x, y)
    click()
    press('.')
    press('escape')


def upgrade_bot(position):
    x = position[0]
    y = position[1]
    move_cursor(x, y)
    click()
    press('/')
    press('escape')
    

# navigates from main menu to one of the expert map screens
def nav_main_to_expert():
    wa.SetCursorPos(CONST_PLAY_BTN_LOC)
    click()
    slp = random.randrange(904, 1473)
    sleep(slp / 1000)
    wa.SetCursorPos(CONST_EXPERT_BTN_LOC)
    click()
    sleep(0.3)

def nav_victory_to_main():
    wa.SetCursorPos(CONST_NEXT_BTN_LOC)
    click()
    slp = random.randrange(904, 1473)
    sleep(slp / 1000)
    wa.SetCursorPos(CONST_HOME_BTN_LOC)
    click()
    sleep(5)


def open_chest():
    wa.SetCursorPos(CONST_CHEST_BTN_LOC)
    click()
    sleep(0.3)
    wa.SetCursorPos(CONST_INSTA1_BTN_LOC)
    click()
    sleep(0.3)
    click()
    sleep(0.3)
    wa.SetCursorPos(CONST_INSTA2_BTN_LOC)
    click()
    sleep(0.3)
    click()
    sleep(0.3)
    wa.SetCursorPos(CONST_CONTINUE_BTN_LOC)
    click()
    sleep(0.3)
    press('escape')
    sleep(0.3)
    wa.SetCursorPos(CONST_CANCEL_BTN_LOC)
    click()
    sleep(0.3)


def move_cursor(x, y):
    wa.SetCursorPos([x, y])


def place_monkey(monkey, x, y):
    move_cursor(x, y)
    monkey_list = {"dart": 'q', "hero": 'u', "sub": 'x', "sniper": 'z', "spac": 'j', "wizard": 'a', "alch": 'f'}
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


# returns current cash or -1 if OCR fails
def find_cash():
    take_screenshot()
    screenshot = cv.imread("monitor-1.png")
    gray = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    cash_crop = thresh[20:65, 347:500]  # crop & convert bgr -> rgb
    tesseract_out = pytesseract.image_to_string(cash_crop, config="--psm 13")  # Tesseract does its best to recognise something
    print("ocr out")
    print(tesseract_out)
    found_cash_list = [s for s in list(tesseract_out) if s.isdigit()]  # Find digits in what was recognised
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


def wait_for_victory(seconds):
    sleep(seconds)
    

def solve_infernal():
    place_monkey("dart", 836, 387)


def solve_quad():
    return


def solve_dark_castle():
    place_monkey("dart", 577, 491)
    wait_for_cash(920)
    place_monkey("hero", 910, 144)
    wait_for_cash(170)
    place_monkey("sub", 1083, 694)
    wait_for_cash(380)
    upgrade_bot(placed_monkeys["sub"])
    wait_for_cash(850)
    upgrade_bot(placed_monkeys["sub"])
    wait_for_cash(535)
    upgrade_top(placed_monkeys["sub"])
    upgrade_top(placed_monkeys["sub"])
    wait_for_cash(245)
    upgrade_bot(placed_monkeys["dart"])
    upgrade_bot(placed_monkeys["dart"])
    wait_for_cash(935)
    upgrade_bot(placed_monkeys["sub"])
    wait_for_cash(2550)
    upgrade_bot(placed_monkeys["sub"])
    wait_for_cash(530)
    upgrade_bot(placed_monkeys["dart"])
    wait_for_cash(470)
    place_monkey("alch", 924, 666)
    wait_for_cash(1700)
    upgrade_top(placed_monkeys["alch"])
    upgrade_top(placed_monkeys["alch"])
    upgrade_top(placed_monkeys["alch"])
    wait_for_cash(615)
    upgrade_mid(placed_monkeys["alch"])
    upgrade_mid(placed_monkeys["alch"])
    wait_for_cash(2550)
    upgrade_top(placed_monkeys["alch"])
    
    # just in case
    wait_for_cash(7000)
    upgrade_bot(placed_monkeys["sub"])
    upgrade_top(placed_monkeys["alch"])

    wait_for_victory(85)




print("The program will take single screenshots of your first monitor for navigation purposes\n")

find_cash()

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
    click()
    sleep(0.3)
    take_screenshot()
    # read in screenshot from file in grayscale
    menu_screenshot = cv.imread("monitor-1.png", cv.IMREAD_GRAYSCALE)
    match = match_template(menu_screenshot, CONST_BONUS_TEMPLATE)
else:
    # wa.SetCursorPos(match)

    # hardcoded dark castle
    click()
    sleep(0.3)
    move_cursor(950,260)

    click()
    sleep(0.3)
    move_cursor(632, 582)
    click()
    sleep(0.3)
    click()
    sleep(5)
    start_game()
    solve_dark_castle()
    nav_victory_to_main()
    # solve_infernal()
    open_chest()

# writes screen
# cv.imwrite('res.png', screenshot)
# opens image for debugging lole
# plt.imshow(screenshot), plt.show()
