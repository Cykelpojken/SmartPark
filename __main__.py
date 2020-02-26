from car_controller.car_controller_ import CarController
import numpy as np
import config as cfg
import image_processing as ip
import time
import cv2
import zmq

MAP_SIZE_PIXELS         = cfg.MAP_SIZE_PIXELS

c = CarController("localhost")
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % 5555)

while True:
    if c.slam_data_model.x is not None:
        mapimg = np.reshape(np.frombuffer(c.slam_data_model.mapbytes, dtype=np.uint8), (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS))
        #print(len(mapimg.to_bytes()))
        cv2.imwrite("map.jpg", mapimg)
        #print(c.slam_data_model.mapbytes)
        t_map = ip.thresholding(mapimg)
        d_map = ip.dilation(t_map)
        e_map =  ip.erosion(d_map)
        blur = ip.blur(e_map, 3, 0)
        identified, coordinates = ip.find_spot(blur)
        display_image = identified
        #print(identified)
        # print(display_image.shape[0])
        # print(display_image.shape[1])
        send_bytes =display_image.shape[0].to_bytes(2, 'big') + display_image.shape[1].to_bytes(2, 'big') + display_image.tobytes()
        #print(len(send_bytes))
        socket.send(send_bytes)
        #print("sent image")

        time.sleep(0.1)
        
    else:
        # mapimg2 = cv2.imread("map.jpg", 0)
        # print("asd")
        # t_map = ip.thresholding(mapimg2)
        # d_map = ip.dilation(t_map)
        # e_map =  ip.erosion(d_map)
        # blur = ip.blur(e_map)
        # identified, coordinates = ip.find_spot(blur)
        #ip.find_spot()
        print("sleeping 1 sec")
        time.sleep(1)
