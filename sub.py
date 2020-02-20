import zmq
import cv2
import numpy as np
from roboviz import MapVisualizer
import config as cfg

MAP_SIZE_PIXELS         = cfg.MAP_SIZE_PIXELS
MAP_SIZE_METERS         = cfg.MAP_SIZE_METERS
MAP_SIZE_PIXELS_1       = 1118
DEFAULT_SLAM_MAP        = False

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect ("tcp://test.local:5555")
socket.setsockopt(zmq.SUBSCRIBE, b'')

viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM') if DEFAULT_SLAM_MAP else MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_PIXELS_1, MAP_SIZE_METERS, 'SLAM')

while True:
    pic = socket.recv()
    x = int.from_bytes(pic[:2], 'big')
    y = int.from_bytes(pic[2:4], 'big')
    pic = np.frombuffer(pic[4:], dtype = 'uint8')
    pic = pic.reshape(x, y)
    if not viz.display(x/1000., y/1000.,0, pic):
        exit()
    else:
        cv2.imwrite("demo.jpg", pic)
    