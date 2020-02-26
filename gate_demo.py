from car_controller.car_controller_ import CarController
import numpy as np
import config as cfg
import image_processing as ip
import time
import cv2
import zmq
import struct


MAP_SIZE_PIXELS         = cfg.MAP_SIZE_PIXELS

c = CarController("localhost")
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % 5555)

while True:
    if c.slam_data_model.x is not None:
        mapimg = np.reshape(np.frombuffer(c.slam_data_model.mapbytes, dtype=np.uint8), (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS))
        display_image = mapimg
        t_map = ip.thresholding(mapimg)
        d_map = ip.dilation(t_map)
        t_e_map =  ip.erosion(d_map)
        blur = ip.blur(t_e_map)
        #identified, coordinates = ip.find_spot(blur)
        #display_image = identified
        print("X: {}".format(c.slam_data_model.x/100))
        print("Y: {}".format(c.slam_data_model.y/100))
        print("Theta: {}".format(c.slam_data_model.theta))
        print("-----------------------------------------")
        send_bytes = display_image.shape[0].to_bytes(2, 'big') + display_image.shape[1].to_bytes(2, 'big') + bytearray(struct.pack("f", c.slam_data_model.theta)) + display_image.tobytes()
        socket.send(send_bytes)
        time.sleep(0.1)
    else:
        print("sleeping 1 sec")
        time.sleep(1)