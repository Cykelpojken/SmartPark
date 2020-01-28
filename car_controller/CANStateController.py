from car_controller.CANStateModel import CANStateModel
from car_controller.ConfigModel import ConfigModel
import zmq
import time

class CANStateController:
    def __init__(self,
                 can_state_model: CANStateModel,
                 config_model: ConfigModel,
                 context: zmq.Context):
        self.can_state_model = can_state_model
        self.subscriber_socket = context.socket(zmq.SUB)
        self.config_model = config_model
        self.conf_sub(self.subscriber_socket, 
                      b"", 
                      f"tcp://{self.config_model.address}:{self.config_model.can_port}")


    def conf_sub(self, socket, filter_bytes, address):
        socket.setsockopt(zmq.RCVHWM, 1)
        socket.setsockopt(zmq.RCVTIMEO, 1000)
        socket.setsockopt(zmq.SUBSCRIBE, filter_bytes)
        print(address)
        socket.connect(address)


    def recv_data(self):
        try:
            data = self.subscriber_socket.recv()
            self.can_state_model.populate_from_proto(data)
        except zmq.error.Again:
            time.sleep(1)

    def recv_loop(self):
        while True:
            self.recv_data()