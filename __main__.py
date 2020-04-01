from car_controller.CarController import CarController
import numpy as np
import config as cfg
import image_processing as ip
import time
import cv2
import zmq
import math

from rplidar import RPLidar as Lidar
from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel

MAP_SIZE_PIXELS         = cfg.MAP_SIZE_PIXELS
MAP_SIZE_METERS         = cfg.MAP_SIZE_METERS
BLURMAP                 = 7

c = CarController(address='trevor.local')
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.setsockopt(zmq.SNDHWM, 10)
socket.bind("tcp://*:%s" % 5558)
prev_cords = [0,0]

MIN_SAMPLES = 20

lidar = Lidar('/dev/ttyUSB0')
slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

trajectory = []

# Initialize empty map
mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

# Create an iterator to collect scan data from the RPLidar
iterator = lidar.iter_scans()


# We will use these to store previous scan in case current scan is inadequate
previous_distances = None
previous_angles    = None

# First scan is crap, so ignore it
next(iterator)
sub_count = 0
while True:

    # Extract (quality, angle, distance) triples from current scan
    items = [item for item in next(iterator)]


    # Extract distances and angles from triples
    distances = [item[2] for item in items]
    angles    = [item[1] for item in items]

    # Update SLAM with current Lidar scan and scan angles if adequate
    if len(distances) > MIN_SAMPLES:

        slam.update(distances, scan_angles_degrees=angles)
        previous_distances = distances.copy()
        previous_angles    = angles.copy()

    # If not adequate, use previous
    elif previous_distances is not None:
        slam.update(previous_distances, scan_angles_degrees=previous_angles)

    # Get current robot position
    x, y, theta = slam.getpos()

    # Get current map bytes as grayscale
    slam.getmap(mapbytes)

    #Display map and robot pose, exiting gracefully if user closes it
    # if not (viz.display(x/1000., y/1000., -theta + 180, mapbytes)):
    #     exit(0)
    print("X: " + str(x/cfg.MAP_SIZE_METERS))
    print("Y:" + str(y/cfg.MAP_SIZE_METERS))
    print("Theta:" + str(theta))
    print("---------------------------------------------")
    display_image = np.reshape(np.frombuffer(mapbytes, dtype=np.uint8), (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS))
    if sub_count >= 3:
        send_bytes =display_image.shape[0].to_bytes(2, 'big') + display_image.shape[1].to_bytes(2, 'big') + int(math.floor(x)).to_bytes(2, 'big') + int(math.floor(y)).to_bytes(2, 'big') + int(math.floor(abs(theta))).to_bytes(2, 'big') + display_image.tobytes()
        socket.send(send_bytes)
    sub_count += 1
    
# while True:
#     if c.slam_data_model.x is not None:
#         if c.slam_data_model.x/MAP_SIZE_METERS != prev_cords[0] or c.slam_data_model.y/MAP_SIZE_METERS != prev_cords[1]:
#             prev_cords[0] = c.slam_data_model.x/MAP_SIZE_METERS
#             prev_cords[1] = c.slam_data_model.y/MAP_SIZE_METERS
#             print(c.slam_data_model.x/MAP_SIZE_METERS, c.slam_data_model.y/MAP_SIZE_METERS)
#         print(c.slam_data_model.theta)
#         mapimg = np.reshape(np.frombuffer(c.slam_data_model.mapbytes, dtype=np.uint8), (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS))
#         cv2.imwrite("map.png", mapimg)
#         t_map = ip.thresholding(mapimg)
#         d_map = ip.dilation(t_map)
#         e_map =  ip.erosion(d_map)
#         blur = ip.blur(e_map, BLURMAP, 0)
#         identified, coordinates = ip.find_spot(blur)
#         display_image = mapimg
#         # if coordinates is not None:
#         #     print("-----------------------------------------")
#         #     print ("parking coordinates: {}    {} ". format(coordinates[0], coordinates[1]))
#         #     print("-----------------------------------------")

#         send_bytes =display_image.shape[0].to_bytes(2, 'big') + display_image.shape[1].to_bytes(2, 'big') + display_image.tobytes()
#         socket.send(send_bytes)

#         time.sleep(0.1)
        
#     else:
#         # mapimg2 = cv2.imread("map.jpg", 0)
#         # print("asd")
#         # t_map = ip.thresholding(mapimg2)
#         # d_map = ip.dilation(t_map)
#         # e_map =  ip.erosion(d_map)
#         # blur = ip.blur(e_map)
#         # identified, coordinates = ip.find_spot(blur)
#         #ip.find_spot()
#         #print(MATCHES)
#         print("sleeping 1 sec")
#         time.sleep(1)
