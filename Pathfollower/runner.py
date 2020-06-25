import cv2
import numpy as np
import threading
import pathfinder3 as pf
import colorsys
import time
import math
import random
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
waypoints = []
start = (0, 0)
end = (0, 0)
rw = 3
p = 0
def mouse_event(event, pX, pY, flags, param):

    global img, start, end, p

    if event == cv2.EVENT_LBUTTONUP:
        if p == 0:
            cv2.rectangle(img, (pX - rw, pY - rw),
                        (pX + rw, pY + rw), (0, 255, 0), -1)
            start = (pX, pY)
            print("start = ", start)
            p += 1
        elif p == 1:
            cv2.rectangle(img, (pX - rw, pY - rw),
                        (pX + rw, pY + rw), (0, 0, 255), -1)
            end = (pX, pY)
            print("end = ", end)
            p += 1


def disp():
    global img
    cv2.imshow("Image", img)
    cv2.setMouseCallback('Image', mouse_event)
    while True:
        cv2.imshow("Image", img)
        cv2.waitKey(15)

img = cv2.imread(config["FIELD_IMAGE"]["FILE_LOCATION"], cv2.IMREAD_GRAYSCALE)
_, img = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY)
img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
#matrix = img[:,:,0]
#print(matrix)


print("Select start and end points : ")

t = threading.Thread(target=disp, args=())
t.daemon = True
t.start()

while p < 2:
    pass
algchoice = input("Select your choice of algorithm (BFS or astar) : ")
pathfinder2 = pf.Pathfinder(img, algchoice, start, end)
waypoints = pathfinder2.findpath()
print (waypoints)
#start = Point(530, 800)
#end = Point(380, 280)


cv2.waitKey(0)