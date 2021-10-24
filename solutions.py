from time import sleep

import cv2 as cv
import pytesseract

import utils

placed_monkeys = {}


def start_game():
    utils.press('space')
    sleep(0.5)
    utils.press('space')


def upgrade_top(position):
    x = position[0]
    y = position[1]
    utils.move_cursor(x, y)
    utils.click()
    utils.press(',')
    utils.press('escape')


def upgrade_mid(position):
    x = position[0]
    y = position[1]
    utils.move_cursor(x, y)
    utils.click()
    utils.press('.')
    utils.press('escape')


def upgrade_bot(position):
    x = position[0]
    y = position[1]
    utils.move_cursor(x, y)
    utils.click()
    utils.press('/')
    utils.press('escape')


# returns current cash or -1 if OCR fails
def find_cash():
    utils.take_screenshot()
    screenshot = cv.imread("monitor-1.png")
    gray = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    cash_crop = thresh[20:65, 347:500]
    custom_oem_psm_config = r'--oem 3 --psm 13'
    tesseract_out = pytesseract.image_to_string(cash_crop, config=custom_oem_psm_config)  # Tesseract does its best to recognise something
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


# returns current round or -1 if OCR fails
def find_round():
    utils.take_screenshot()
    screenshot = cv.imread("monitor-1.png")
    gray = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    round_crop = thresh[30:65, 1430:1485]  # crop
    cv.imwrite('round.png', round_crop)    
    custom_oem_psm_config = r'--oem 3 --psm 13'
    tesseract_out = pytesseract.image_to_string(round_crop, config=custom_oem_psm_config)  # Tesseract does its best to recognise something
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
        print("current round: " + str(current_round) + " = " + str(number))
        return


def wait_for_victory(seconds):
    sleep(seconds)
    

def place_monkey(monkey, x, y):
    utils.move_cursor(x, y)
    monkey_list = {"dart": 'q', "hero": 'u', "sub": 'x', "sniper": 'z', "spac": 'j', "wizard": 'a', "alch": 'f'}
    desired_key = monkey_list[monkey]
    utils.press(desired_key)
    utils.click()
    placed_monkeys.update({monkey: (x, y)})


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
    wait_for_cash(6000)
    upgrade_bot(placed_monkeys["sub"])
    upgrade_top(placed_monkeys["alch"])
    wait_for_round(39)
    wait_for_victory(27)


    