import zmq
import cv2
import numpy as np
from roboviz import MapVisualizer
import config as cfg
from car_controller.CarController import CarController
import threading
import time
import matplotlib.pyplot as plt
from nav_msgs.msg import OccupancyGrid
class sub:

    def __init__(self):
        context = zmq.Context()
        self.pos_socket_init(context)
        self.map_socket_init(context)

    def pos_socket_init(self, context):
        self.pos_socket = context.socket(zmq.SUB)
        self.pos_socket.connect("tcp://192.168.150.154:5560")
        self.pos_socket.setsockopt(zmq.SUBSCRIBE, b'')
        self.pos_socket.setsockopt(zmq.RCVHWM, 2)
        self.pos_socket.setsockopt(zmq.RCVBUF, 1024)

    def map_socket_init(self, context):
        self.map_socket = context.socket(zmq.SUB)
        self.map_socket.connect("tcp://192.168.150.154:5555")
        self.map_socket.setsockopt(zmq.SUBSCRIBE, b'')
        self.map_socket.setsockopt(zmq.RCVHWM, 2)
        self.map_socket.setsockopt(zmq.RCVBUF, 1024)

    def init_viz(self, width, height):
        return MapVisualizer(int(width), int(height))

    def pos_thread(self):
        while True:
            pos = self.pos_socket.recv()
            pos = pos.decode('ASCII')
            pos = pos.split(":")

            self.x_coordinate = pos[0]
            self.y_coordinate = pos[1]
            #print(self.x_coordinate, self.y_coordinate)

            time.sleep(0.1)

    # def map_thread(self):
    #     while True:
    #         data = self.map_socket.recv()
    #         occupancy_object = OccupancyGrid()
    #         OccupancyGrid.deserialize(occupancy_object, data)

    #         self.height = occupancy_object.info.height
    #         self.width = occupancy_object.info.width
            
    #         img = list(occupancy_object.data)

    #         img = [x + 1 for x in img]
    #         for p, x in enumerate(img):
    #                 img[p] = 255 - x
    #                 if img[p] == 255:
    #                     img[p] = 255 - 50

    #         self.map = bytearray(img)
    #         mapimg = np.reshape(np.frombuffer(self.map, dtype=np.uint8), (int(height), int(width)))
    #         cv2.imwrite("asd.png", mapimg)

           

if __name__ == "__main__":
    sub = sub()
    threading.Thread(target = sub.map_thread, daemon=False).start()
    threading.Thread(target= sub.pos_thread, daemon=False).start()
    time.sleep(0.2)
    viz = sub.init_viz(200, 200)
    while True:
        try:
            #print(time.time() - t1) 
            viz.display(0, 0, 0, sub.map)

        except Exception as e:
            plt.close()
            viz = sub.init_viz(sub.height, sub.width)



