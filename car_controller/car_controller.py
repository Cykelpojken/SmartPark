from car_controller.StateModel import StateModel, Signal
from car_controller.NetworkStateSubscriber import NetworkStateSubscriber
from car_controller.NetworkCommandSender import NetworkCommandSender
from car_controller.CANFramesModel import CANFramesModel
from car_controller.CameraReceiver import CameraReceiver
from car_controller.ZmqModel import ZmqModel
from car_controller.SlamDataModel import SlamDataModel
from car_controller.ConfigModel import ConfigModel
from car_controller.LidarScanModel import LidarScanModel
from car_controller.CANStateModel import CANStateModel

from car_controller.LidarController import LidarController
from car_controller.SlamController import SlamController
from car_controller.RemoteSlamController import RemoteSlamController
from car_controller.CANStateController import CANStateController

from queue import Queue
import threading
import time

# TODO: dictionary lookup of signal IDs instead of numbers

class CarController:
    def __init__(self, address):
        self.signal_queue = Queue()

        self.zmq_model = ZmqModel()
        self.lidar_scan_model = LidarScanModel()
        self.config_model = ConfigModel()
        self.config_model.address = address
        self.slam_data_model = SlamDataModel()
        self.can_state_model = CANStateModel()
        self.state_model = StateModel(44)

        self.camera_receiver = CameraReceiver(self.config_model.address,
				 	      self.zmq_model,
					      self.config_model)

        self.lidar_controller = LidarController(self.lidar_scan_model,
                                                self.config_model,
                                                self.zmq_model.context)

        if self.config_model.use_local_slam:
            self.slam_controller = SlamController(self.lidar_scan_model,
                                                 self.slam_data_model)
        else:
            self.slam_controller = RemoteSlamController(self.slam_data_model,
                                                        self.config_model.lidar_server_address)

        self.can_state_controller = CANStateController(self.can_state_model,
                                                       self.config_model,
                                                       self.zmq_model.context)


        self.network_state_subscriber = NetworkStateSubscriber(self.state_model, self.config_model.address)
        self.network_command_sender = NetworkCommandSender(self.signal_queue, self.config_model.address)

    def queue_state(self, signal_id, data):
        self.signal_queue.put(Signal(signal_id, data, time.time()), block=True)

    def arm_motors(self):
        self.queue_state(44, 3)

    def disarm_motors(self):
        self.queue_state(44, 0)

    def set_speed(self, speed):
        self.queue_state(22, speed)

    def set_turnrate(self, turn):
        self.queue_state(23, turn)

    def get_current(self):
        self.state_model.get_signal(5)

    def get_voltage(self):
        self.state_model.get_signal(46)

    def get_compass(self):
        raise NotImplementedError()

    def get_wheel_speeds(self):
        return(self.state_model.get_signal(x) for x in range(1,5))

    def get_picture(self):
        self.camera_receiver.get_picture()

    def get_lidar(self):
        if time.time() - self.lidar_scan_model.timestamp > 1:
             print("Warning: using lidar data older than 1 second.")
        return self.lidar_scan_model.scan_data

    def get_sonar(self, id):
        raise NotImplementedError()



    def heartbeat_thread(self):
        """Thread method for sending regular heartbeat."""
        i = 0
        while True:
            self.queue_state(35, 1)
            self.queue_state(34, i)
            time.sleep(1)
            i = (i+1)%221

    def start(self):
        threading.Thread(target=self.heartbeat_thread, daemon=True).start()
        self.network_state_subscriber.start()
        self.network_command_sender.start()
        print("Car controller init OK!")
