import zmq
import time
import car_controller.signal_protobuf_pb2 as pb
import threading

COMMAND_PORT = 5555

class NetworkCommandSender:

    def __init__(self, signal_queue, address):
        self.context = zmq.Context()
        self.command_socket = self.context.socket(zmq.REQ)
        self.command_socket.setsockopt(zmq.RCVHWM, 1)
        self.command_socket.setsockopt(zmq.SNDHWM, 1)
        self.command_socket.connect("tcp://"+address+':'+str(COMMAND_PORT))

        self.signal_queue = signal_queue

    def send_signal(self, signal_data):
        try:
            pb_signal = pb.Signal()
            pb_signal.id = signal_data.id
            pb_signal.float_data = signal_data.data

            self.command_socket.send(pb_signal.SerializeToString())
            reply = self.command_socket.recv()
        except Exception as e: 
            print(e)

    def send_loop(self):
        while True:
            """
            Fetch signal values here from a queue at CarController.
            """
            signal_data = self.signal_queue.get(block=True)
            self.send_signal(signal_data)

    def start(self):
        threading.Thread(target=self.send_loop, daemon=True).start()
