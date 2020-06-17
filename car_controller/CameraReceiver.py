import socket
import threading
import time
import io
from PIL import Image
import zmq
from queue import Queue
from PyQt5 import QtCore, QtGui, QtWidgets
import car_controller.signal_protobuf_pb2 as pb
from car_controller.ZmqModel import ZmqModel
from car_controller.ConfigModel import ConfigModel

class CameraReceiver():
    def __init__(self, address, zmq_model: ZmqModel, config_model: ConfigModel):
        self.context = zmq_model.context
        self.sensor_socket = self.context.socket(zmq.SUB)

        # Configure subscribe sockets     
        self.sensor_socket.setsockopt(zmq.RCVHWM, 1)
        self.sensor_socket.setsockopt(zmq.RCVTIMEO, 1000)
        self.sensor_socket.setsockopt(zmq.SUBSCRIBE, b'')
        self.sensor_socket.connect("tcp://"+address+":" + str(config_model.camera_port))

    def get_picture(self, camera_id=0):
        img_proto = pb.Image()
        raw_img_bytes = self.get_sensor_data(self.sensor_socket)
        if raw_img_bytes is not None:
            try:
                img_proto.ParseFromString(raw_img_bytes)
                temp_image = Image.open(io.BytesIO(img_proto.image_data))
            except OSError:
                print("Received invalid image! Len: len(%s)" % len(img_proto.image_data))
        else:   
            print("Got None img") 
            return None
        return temp_image

    def get_sensor_data(self, sock):
        """
        * Retreives the data from a message. 
        * @param The socket to receive from
        * @return The data portion of a Message. The data portion is usually another Message object.
        """        
        try:
            img = sock.recv()
            return img
        except zmq.error.Again:
            print("Timeout receiving image from socket")
            return None
