#!/usr/bin/env python3


MAP_SIZE_PIXELS         = 500*2
MAP_SIZE_METERS         = 10*2
LIDAR_DEVICE        = '/dev/ttyUSB1'


MIN_SAMPLES   = 50

from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar
from rplidar import RPLidarException
import numpy as np
import cv2
import time
import zmq
import image_processing as ip


if __name__ == '__main__':

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % 5555)

    # Connect to Lidar unit
    try: 
        lidar = Lidar(LIDAR_DEVICE)
    except: 
        LIDAR_DEVICE        = '/dev/ttyUSB0'
        lidar = Lidar(LIDAR_DEVICE)
    lidar.stop()

    # Create an RMHC SLAM object with a laser model and optional robot model
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

    # Initialize an empty trajectory
    trajectory = []

    # Initialize empty map
    mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

    lidar.set_pwm(500)

    # Create an iterator to collect scan data from the RPLidar
    iterator = lidar.iter_scans(1000)

    # We will use these to store previous scan in case current scan is inadequate
    previous_distances = None
    previous_angles    = None

    # First scan is crap, so ignore it
    try:
        next(iterator)
    except RPLidarException:
        pass

    while True:

        items = next(iterator)
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
        print(f"{x}, {y}")

        # Get current map bytes as grayscale
        slam.getmap(mapbytes)

        # Display map and robot pose, exiting gracefully if user closes it
        #if not viz.display(x/1000., y/1000., theta, mapbytes):
            #exit(0)
        t1 = time.time()
        mapimg = np.reshape(np.frombuffer(mapbytes, dtype=np.uint8), (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS))
        display_image = mapimg
        t_map = ip.thresholding(mapimg)
        d_map = ip.dilation(t_map)
        t_e_map =  ip.erosion(d_map)
        blur = ip.blur(t_e_map)
        coordinates = ip.find_spot(blur)
        # display_image = identified
        send_bytes = display_image.shape[0].to_bytes(2, 'big') + display_image.shape[1].to_bytes(2, 'big') + display_image.tobytes()
        socket.send(send_bytes)
        print("sent image")
        t2 = time.time()
        print(t2-t1)
        time.sleep(0.1)

 
    # Shut down the lidar connection
    lidar.stop()
    lidar.disconnect()
