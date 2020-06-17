from car_controller.SlamDataModel import SlamDataModel
import car_controller.slam_proto_pb2 as slam_pb
import zmq
import threading
import time

class RemoteSlamController():
    def __init__(self,
                 slam_data_model: SlamDataModel,
                 slam_Server_address):
        self.slam_Server_address = slam_Server_address
        self.active = True
        self.slam_map_pb = slam_pb.SlamMap()
        self.slam_data_model = slam_data_model
        context = zmq.Context()
        self.map_socket_init(context)
        threading.Thread(target = self.receive_slam_thread, daemon=True).start()

    def map_socket_init(self, context):
        self.map_socket = context.socket(zmq.SUB)
        self.map_socket.connect("tcp://" + self.slam_Server_address + ":5555")
        self.map_socket.setsockopt(zmq.SUBSCRIBE, b'')
        self.map_socket.setsockopt(zmq.RCVHWM, 2)
        self.map_socket.setsockopt(zmq.RCVBUF, 1024)

    def receive_slam_thread(self):
        while True:
            if self.active:
                data = self.map_socket.recv()
                self.slam_map_pb.ParseFromString(data)

                self.slam_data_model.set_position(self.slam_map_pb.x,
                                                  self.slam_map_pb.y,
                                                  self.slam_map_pb.theta)

                self.slam_data_model.set_map(bytearray(self.slam_map_pb.grid))
                self.slam_data_model.set_map_dimentions(self.slam_map_pb.width, self.slam_map_pb.height)
            else:
                time.sleep(1)

    def set_active(self, state):
        self.active = state
