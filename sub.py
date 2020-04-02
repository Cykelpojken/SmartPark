import zmq
import cv2
import numpy as np
from roboviz import MapVisualizer
import config as cfg
from car_controller.CarController import CarController
import threading
import time

MAP_SIZE_PIXELS = cfg.MAP_SIZE_PIXELS
MAP_SIZE_METERS = cfg.MAP_SIZE_METERS
MAP_SIZE_PIXELS_1 = 1118
DEFAULT_SLAM_MAP = True

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://trevor.local:5558")
socket.setsockopt(zmq.SUBSCRIBE, b'')
socket.set_hwm(1)
# socket.setsockopt(zmq.RCVHWM, 1)

c = CarController(address='trevor.local')
viz = None
def init_map():
    if DEFAULT_SLAM_MAP:
        return MapVisualizer(MAP_SIZE_PIXELS,
                             MAP_SIZE_PIXELS,
                             MAP_SIZE_METERS,
                             'SLAM')
    else:
        return MapVisualizer(MAP_SIZE_PIXELS,
                             MAP_SIZE_PIXELS_1,
                             MAP_SIZE_METERS,
                             'SLAM')


while True:
    pic = socket.recv()

    x_pic = int.from_bytes(pic[:2], 'big')
    y_pic = int.from_bytes(pic[2:4], 'big')
    x_coordinate = int.from_bytes(pic[4:6], 'big') / cfg.MAP_SIZE_METERS
    y_coordinate = int.from_bytes(pic[6:8], 'big') / cfg.MAP_SIZE_METERS
    theta = int.from_bytes(pic[8:10], 'big')

    if viz is None or DEFAULT_SLAM_MAP is False and y_pic != MAP_SIZE_PIXELS_1:
        MAP_SIZE_PIXELS_1 = y_pic
        viz = init_map()

    pic = np.frombuffer(pic[10:], dtype='uint8')
    pic = pic.reshape(x_pic, y_pic)

    if not viz.display(x_coordinate/100, y_coordinate/100, theta - 180, pic):
        exit()
    else:
        pass
        # print("BEFORE: " + str(c.slam_data_model.x/25), str(c.slam_data_model.y/25))
