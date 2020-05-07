from car_controller.CarController import CarController
import numpy as np  # pragma: no cover
import config as cfg
import image_processing as ip
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
        self.c = CarController(address='trevor.local')
        self.BLURMAP = 7
        self.prev_cords = [0, 0]
        self.MIN_SAMPLES = 20
        self.trajectory = []
        self.previous_distances = None
        self.previous_angles = None

        self.sub_count = 0
        self.init_zmq()
        #self.init_lidar()
        self.init_slam()
        
    def init_zmq(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.setsockopt(zmq.SNDHWM, 10)
        self.socket.bind("tcp://*:%s" % 5558)
    
    def init_lidar(self):
        self.lidar = Lidar('/dev/ttyUSB0')
        self.iterator = self.lidar.iter_scans()
        # First scan is crap, so ignore it
        time.sleep(0.5)
        next(self.iterator)

    def init_slam(self):
        self.MAP_SIZE_PIXELS = cfg.MAP_SIZE_PIXELS
        self.MAP_SIZE_METERS = cfg.MAP_SIZE_METERS
        self.slam = RMHC_SLAM(LaserModel(), self.MAP_SIZE_PIXELS, self.MAP_SIZE_METERS)
        self.mapbytes = bytearray(self.MAP_SIZE_PIXELS * self.MAP_SIZE_PIXELS)


    def main_loop(self):
        while True:
            self.img_test()
            display_image = np.reshape(
                 np.frombuffer(self.c.slam_data_model.mapbytes, dtype=np.uint8),
                 (self.MAP_SIZE_PIXELS, self.MAP_SIZE_PIXELS))
            print(self.c.slam_data_model.mapbytes)
            cv2.imwrite("map.jpg", display_image)
        
    def img_test(self):
        mapimg = cv2.imread("asd.png", 0)
        t_map = ip.thresholding(mapimg)
        d_map = ip.dilation(t_map)
        e_map =  ip.erosion(d_map)
        blur = ip.blur(e_map)
        cv2.imwrite("asd2.png", blur)


            # # Extract (quality, angle, distance) triples from current scan
            # items = [item for item in next(self.iterator)]

            # # Extract distances and angles from triples
            # distances = [item[2] for item in items]
            # angles = [item[1] for item in items]

            # # Update SLAM with current Lidar scan and scan angles if adequate
            # if len(distances) > self.MIN_SAMPLES:

            #     self.slam.update(distances, scan_angles_degrees=angles)
            #     self.previous_distances = distances.copy()
            #     self.previous_angles = angles.copy()

            # # If not adequate, use previous
            # elif self.previous_distances is not None:
            #     self.slam.update(self.previous_distances, scan_angles_degrees=self.previous_angles)

            # # Get current robot position
            # x, y, theta = self.slam.getpos()

            # # Get current map bytes as grayscale
            # self.slam.getmap(self.mapbytes)

            # # Display map and robot pose, exiting gracefully if user closes it
            # # if not (viz.display(x/1000., y/1000., -theta + 180, mapbytes)):
            # #     exit(0)
            # print("X: " + str(x/cfg.MAP_SIZE_METERS))
            # print("Y:" + str(y/cfg.MAP_SIZE_METERS))
            # print("Theta:" + str(theta))
            # print("---------------------------------------------")
            # display_image = np.reshape(
            #     np.frombuffer(self.mapbytes, dtype=np.uint8),
            #     (self.MAP_SIZE_PIXELS, self.MAP_SIZE_PIXELS))

            # if self.sub_count >= 3:
            #     send_bytes = display_image.shape[0].to_bytes(2, 'big') + \
            #         display_image.shape[1].to_bytes(2, 'big') + \
            #         int(math.floor(x)).to_bytes(2, 'big') + \
            #         int(math.floor(y)).to_bytes(2, 'big') + \
            #         int(math.floor(abs(theta))).to_bytes(2, 'big') +\
            #         display_image.tobytes()
            #     self.socket.send(send_bytes)
            # self.sub_count += 1

if __name__ == "__main__":
    m = Main()
    m.__init__()
    time.sleep(1)
    threading.Thread(target=m.main_loop).start()
