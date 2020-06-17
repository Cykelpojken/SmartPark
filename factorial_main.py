#from car_controller.CarController import CarController
import numpy as np  # pragma: no cover
import config as cfg
import image_processing as ip
import time
import cv2
import zmq
import math
import threading
import factorial.factorial

from rplidar import RPLidar as Lidar
from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel

class Main():

    def __init__(self):
        self.b = True
        self.MIN_SAMPLES = 20
        while self.b == True:
            try:
                self.init_lidar()
                self.b = False
            except Exception as e:
                print(e)
        self.init_slam()
        
    
    def init_lidar(self):
        self.lidar = Lidar('/dev/ttyUSB0')
        self.iterator = self.lidar.iter_scans(1000)
        time.sleep(0.5)
        # First scan is crap, so ignore it
        next(self.iterator)

    def init_slam(self):
        self.MAP_SIZE_PIXELS = cfg.MAP_SIZE_PIXELS
        self.MAP_SIZE_METERS = cfg.MAP_SIZE_METERS
        self.slam = RMHC_SLAM(LaserModel(), self.MAP_SIZE_PIXELS, self.MAP_SIZE_METERS)
        self.mapbytes = bytearray(self.MAP_SIZE_PIXELS * self.MAP_SIZE_PIXELS)
        
    def img_processing(self, mapimg):
        t_map = ip.thresholding(mapimg)
        d_map = ip.dilation(t_map)
        e_map =  ip.erosion(d_map)
        blur = ip.blur(e_map, cfg.MAP_BLUR, t = 0)
        return blur
        #cv2.imwrite("map2.jpg", blur)

    def main_loop(self):
        var = 0
        time_total = 0
        total_matches = 0
        max_matches = 0

        while var < 50:
            # Extract (quality, angle, distance) triples from current scan
            items = [item for item in next(self.iterator)]

            # Extract distances and angles from triples
            distances = [item[2] for item in items]
            angles = [item[1] for item in items]

            # Update SLAM with current Lidar scan and scan angles if adequate
            if len(distances) > self.MIN_SAMPLES:

                self.slam.update(distances, scan_angles_degrees=angles)
                self.previous_distances = distances.copy()
                self.previous_angles = angles.copy()

            # If not adequate, use previous
            elif self.previous_distances is not None:
                self.slam.update(self.previous_distances, scan_angles_degrees=self.previous_angles)

            # Get current robot position
            x, y, theta = self.slam.getpos()

            # Get current map bytes as grayscale
            self.slam.getmap(self.mapbytes)
            mapimg = np.reshape(
                np.frombuffer(self.mapbytes, dtype=np.uint8),
                (self.MAP_SIZE_PIXELS, self.MAP_SIZE_PIXELS))

            
            t1 = time.time()
            blur = self.img_processing(mapimg)
            a, b, matches = ip.find_spot(blur)
            t2 = time.time() - t1

            if matches > max_matches:
                max_matches = matches
            
            time_total += t2
            total_matches += matches
            var += 1

        avg_time = time_total / var
        avg_matches = total_matches / var

        print("avg_matches: " + str(avg_matches))
        print("max_matches: " + str(max_matches))

        print("avg_time: " + str(avg_time))


if __name__ == "__main__":
    fact = factorial()
    #m = Main()
    #time.sleep(1)
    #threading.Thread(target=m.main_loop).start()
