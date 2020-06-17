from car_controller.car_controller import CarController
import numpy as np  # pragma: no cover
import config as cfg
import parking_space_detection as psd
import time
import cv2
import zmq
import math
import threading

from rplidar import RPLidar as Lidar
from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel

class Main():

    def __init__(self):
        self.b = True
        self.c = CarController(address='trevor.local')
        self.prev_cords = [0, 0]
        self.MIN_SAMPLES = 20
        self.MAP_BLUR = cfg.MAP_BLUR
        self.trajectory = []
        self.previous_distances = None
        self.previous_angles = None

        self.sub_count = 0
        self.init_zmq()
        self.init_slam()
        
    def init_zmq(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.setsockopt(zmq.SNDHWM, 10)
        self.socket.bind("tcp://*:%s" % 5558)

    def init_slam(self):
        self.MAP_SIZE_PIXELS = cfg.MAP_SIZE_PIXELS
        self.MAP_SIZE_METERS = cfg.MAP_SIZE_METERS
        self.slam = RMHC_SLAM(LaserModel(), self.MAP_SIZE_PIXELS, self.MAP_SIZE_METERS)
        self.mapbytes = bytearray(self.MAP_SIZE_PIXELS * self.MAP_SIZE_PIXELS)
        
    def img_processing(self, mapimg):
        #mapimg = cv2.imread("map.jpg", 0)
        #t_map = psd.thresholding(mapimg)
        #d_map = psd.dilation(mapimg)
        #e_map =  psd.erosion(d_map)
        blur = psd.blur(mapimg, self.MAP_BLUR, t = 0)
        return blur

    def change_color(self, img):
        for p, x in enumerate(img):
            img[p] = 255 - x
            if img[p] == 255:
                img[p] = 255 - 100 #Make unknown grey
            elif img[p] < 200:
                img[p] = 0

        return img

    def main_loop(self):
        while True:
            print(self.c.slam_data_model.theta)
            mapimg = self.c.slam_data_model.slam_map
            mapimg = self.change_color(mapimg)
            height = self.c.slam_data_model.height
            width = self.c.slam_data_model.width
            #print(mapimg)
            mapimg = np.reshape(
                np.frombuffer(mapimg, dtype=np.uint8),
                (width, height))
            cv2.imwrite("map.png", mapimg)
            time.sleep(0.2)

if __name__ == "__main__":
    m = Main()
    time.sleep(1)
    threading.Thread(target=m.main_loop).start()
