import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from mss import mss
import win32api as wa
from time import sleep
import random as random


def rand_click():
    wa.mouse_event(2, 0, 0)
    slp = random.randrange(97, 205)
    print(slp)
    sleep(slp / 1000)
    wa.mouse_event(4, 0, 0)


def nav_to_expert():
    wa.SetCursorPos([800, 950])
    rand_click()
    slp = random.randrange(904, 1473)
    print(slp)
    sleep(slp / 1000)
    wa.SetCursorPos([1300, 1000])
    rand_click()


print("The program will take single screenshots of your first monitor for navigation purposes\n")
nav_to_expert()
# input("Open BTD6 main menu on monitor 1, then press any key to continue")

with mss() as sct:
    sct.shot()

""" template = cv.imread("bonus.png", 0)  # thing to find
img_rgb = cv.imread("fake.png", 0)   # thing to search through
img_gray = cv.imread("fake.png", cv.IMREAD_GRAYSCALE)
w, h = template.shape[::-1]

res = cv.matchTemplate(img_gray, template, cv.TM_CCOEFF_NORMED)
threshold = 0.8
loc = np.where(res >= threshold)  # tuple of matching coordinates
print(loc)
print(len(loc[0]))
for pt in zip(*loc[::-1]):
    cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

cv.imwrite('res.png', img_rgb)
plt.imshow(img_rgb), plt.show() """

scrn = cv.imread("monitor-1.png", cv.IMREAD_GRAYSCALE)
plt.imshow(scrn), plt.show()
