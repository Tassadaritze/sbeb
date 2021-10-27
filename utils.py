import random
from time import sleep

import keyboard
import win32api as wa
from mss import mss


def move_cursor(x, y):
    wa.SetCursorPos([x, y])


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


# saves screenshot to "monitor-1.png"
def take_screenshot():
    with mss() as sct:
        sct.shot(output="screenshots/monitor1.png")
