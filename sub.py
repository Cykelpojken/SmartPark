import zmq
import cv2
import numpy as np
from roboviz import MapVisualizer
import config as cfg
from car_controller.car_controller_ import CarController
import cv2
import math
import time

MAP_SIZE_PIXELS         = cfg.MAP_SIZE_PIXELS
MAP_SIZE_METERS         = cfg.MAP_SIZE_METERS
MAP_SIZE_PIXELS_1       = 1118
DEFAULT_SLAM_MAP        = False

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect ("tcp://192.168.150.154:5555")
socket.setsockopt(zmq.SUBSCRIBE, b'')


c = CarController(address = '192.168.150.174')
viz = None
def init_map():
    return MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM') if DEFAULT_SLAM_MAP else MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_PIXELS_1, MAP_SIZE_METERS, 'SLAM')


while True:
    pic = socket.recv()
    x = int(pic[1:4], base=10)
    y = int(pic[6:9], base = 10)
    print(x, y)

    print("asd")
    mapimg = np.reshape(np.frombuffer(pic[10:], dtype=np.uint8), (x), y))
    cv2.imwrite("asd.jpg", mapimg)
    print("we cknf donc")
    time.sleep(1)

    # x = int.from_bytes(pic[:2], 'big')
    # y = int.from_bytes(pic[2:4], 'big')
    # print(x, y)
    # if viz == None or DEFAULT_SLAM_MAP == False and y != MAP_SIZE_PIXELS_1:
    #     print("asd")
    #     MAP_SIZE_PIXELS_1 = y
    #     viz = init_map()

    # pic = np.frombuffer(pic[4:], dtype = 'uint8')
    # pic = pic.reshape(x, y)
    # if not viz.display(c.slam_data_model.x/10., c.slam_data_model.y/10.,0, pic):
    #     exit()
    # else:
    #     cv2.imwrite("demo.jpg", pic)
    
