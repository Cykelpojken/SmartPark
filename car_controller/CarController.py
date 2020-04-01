"""Ground station car control object."""

import socket
import threading
import time
import io
from PIL import Image
import zmq
from queue import Queue
import car_controller.signal_protobuf_pb2 as pb
from car_controller.ConfigModel import ConfigModel
from car_controller.ZmqModel import ZmqModel
from car_controller.LidarController import LidarController
from car_controller.LidarScanModel import LidarScanModel
from car_controller.SlamController import SlamController
from car_controller.SlamDataModel import SlamDataModel
from car_controller.CANStateController import CANStateController
from car_controller.CANStateModel import CANStateModel

def conf_sub(sock, address):
    sock.setsockopt(zmq.RCVHWM, 1)
#    sock.setsockopt(zmq.RCVTIMEO, 1000)
    sock.setsockopt(zmq.SUBSCRIBE, b'')
    sock.connect(address)

class CarController:

    outbound_queue = Queue()
    image_stream = io.BytesIO()

    def __init__(self, address='192.168.150.199', context = None):
        self.context = context
        if context is None:
            self.context = zmq.Context()
        
        self.state = {}
            
        self.sensor_socket = self.context.socket(zmq.SUB)
        self.can_data_socket = self.context.socket(zmq.SUB)
        self.command_socket = self.context.socket(zmq.REQ)

        command_address = "tcp://"+address+":5555"
        can_data_address = "tcp://"+address+":5556"
        sensor_address = "tcp://"+address+":5557"
 
        # Configure subscribe sockets
        conf_sub(self.sensor_socket, sensor_address)
        conf_sub(self.can_data_socket, can_data_address)
        
        # Connect client/server socket to send commands
        self.command_socket.setsockopt(zmq.RCVHWM, 1)
        self.command_socket.setsockopt(zmq.SNDHWM, 1)
        self.command_socket.connect(command_address)

        self.zmq_model = ZmqModel()
        self.lidar_scan_model = LidarScanModel()
        self.config_model = ConfigModel()
        self.config_model.address = address
        self.slam_data_model = SlamDataModel()
        self.can_state_model = CANStateModel()

        self.lidar_controller = LidarController(self.lidar_scan_model,
                                                self.config_model,
                                                self.zmq_model.context)
        self.slam_controller = SlamController(self.lidar_scan_model,
                                              self.slam_data_model)

        self.can_state_controller = CANStateController(self.can_state_model,
                                                       self.config_model,
                                                       self.context)
        
        threading.Thread(target=self.heartbeat_thread, daemon=True).start()
        threading.Thread(target=self.can_rx_thread, daemon=True).start()
        # threading.Thread(target=self.flush_messages, daemon=True).start()
        print("Car controller init OK!")

     
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

    def can_rx_thread(self):
        while True:
            self.get_can_data(self.can_data_socket)

    def get_can_data(self, sock):
        """
        * Retreives the data from a message. 
        * @param The socket to receive from
        * @return The data portion of a Message. The data portion is usually another Message object.
        """
        try:
            raw_state = sock.recv() 
            new_state = pb.CAN_Signals()
            new_state.ParseFromString(raw_state)
            for signal in new_state.signals:
                signal_data = signal.float_data
                self.update_state(signal.id, signal_data)
            return self.state
        except zmq.error.Again:
            print("Timeout receiving data from socket")
            return None

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

#    def get_lidar(self, lidar_id=0):
#        string = self.get_sensor_data(self.sensor_socket)
#        if string is not None:
#            points = map(self.decode_lidar_chunk, self.lidar_chunks(string))
#            data = np.array(list(points))*[1, 1/4, 1/64*np.pi/180]
#            return data
#        else:
#            return None

    def update_state(self, signal_id, signal_data):
        self.state[signal_id] = signal_data            

#    def decode_lidar_chunk(self, chunk):
#        """Map a chunk of lidar data into (quality, distance, angle)."""
#        #print("decoding chunk: %s" % chunk)
#        print(chunk)
#        return struct.unpack(">BHH", chunk)

#    def lidar_chunks(self, data):
#        """Generator for getting lidar data one point at a time."""
#        lidar_chunk_size = 5
#        for i in range(0, len(data), lidar_chunk_size):
#            yield data[i:i + lidar_chunk_size]

    def get_wheel_speeds(self):
        fr = self.state[1]
        fl = self.state[2]
        rr = self.state[3]
        rl = self.state[4]
        return [fr, fl, rr, rl]
        

    def get_sonar(self, id):
        sonar_1 = self.state[26]
        sonar_2 = self.state[27]
        sonar_3 = self.state[28]
        sonar_4 = self.state[29]
        return [sonar_1, sonar_2, sonar_3, sonar_4]
        
    def get_voltage(self):
        return self.state[46]
    
    def get_current(self):
        return self.state[5]

    def serialize_state(self, state):
        """Serialize CAN data for communication over Wifi to the client"""
        signaldb_proto = pb.CAN_Signals()
        signaldb_proto.timestamp = time.time()
        for signal_id in state:
            sig_value = state[signal_id]
            signal_proto = signaldb_proto.signals.add()
            signal_proto.id = signal_id
            signal_proto.float_data = sig_value

        return signaldb_proto.SerializeToString()
    """    if type(sig_value) == float:
                signal_proto.float_data = sig_value
            elif type(sig_value) == int:
                signal_proto.int_data = sig_value
            elif type(sig_value) == bool:
                signal_proto.bool_data = sig_value
            elif type(sig_value) == str:
                signal_proto.string_data = sig_value    
        return signaldb_proto.SerializeToString()"""

    def send_state(self, signal_id, data):
        # Wait for next request from client
        try:
            pb_signal = pb.Signal()
            pb_signal.id = signal_id
            pb_signal.float_data = data
            self.command_socket.send(pb_signal.SerializeToString())
            reply = self.command_socket.recv()
        except:
            time.sleep (0.1)

    def arm_motors(self):
        print("A")
        self.send_state(44, 3)

    def disarm_motors(self):
        print("D")
        self.send_state(44, 0)

    def set_speed(self, speed):
        self.send_state(22, speed)

    def set_turnrate(self, rate):
        self.send_state(23, rate)

    def heartbeat_thread(self):
        """Thread method for sending regular heartbeat."""
        i = 0
        while True:
            self.send_state(35, 1)
            self.send_state(34, i)
            time.sleep(1)
            i = (i,i+1)[i<221]   
            try:         
                if self.state[44] == 3:
                    print("Arm")
                else:
                    print("Disarm")
            except Exception as e:
                pass
                #print(e)
