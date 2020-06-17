from car_controller.StateModel import StateModel, Signal

import zmq
import time
import car_controller.signal_protobuf_pb2 as pb
import threading

STATE_PORT = 5556

class NetworkStateSubscriber():
    def __init__(self, state_model: StateModel, address):
        self.state_model = state_model

        self.context = zmq.Context()
        self.command_socket = self.context.socket(zmq.SUB)
        self.command_socket.setsockopt(zmq.RCVHWM, 1)
        self.command_socket.setsockopt(zmq.SUBSCRIBE, b'')
        self.command_socket.connect("tcp://"+address+':'+str(STATE_PORT))

    def receive_packet(self):
        raw_state = self.command_socket.recv()
        updated_state = pb.CAN_Signals()
        updated_state.ParseFromString(raw_state)

        for signal in updated_state.signals:
            signal_tuple = Signal(signal.id, signal.float_data, time.time())
            self.state_model.signals[signal.id] = signal_tuple
        
    def receive_loop(self):
        while True:
            try:
                self.receive_packet()
            except zmq.error.Again:
                print("Timeout receiving data from socket")
                time.sleep(0.001)

    def start(self):
        threading.Thread(target=self.receive_loop, daemon=True).start()
