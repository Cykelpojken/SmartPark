from car_controller.Signal import Signal
import config as cfg
MAP_SIZE_PIXELS         = cfg.MAP_SIZE_PIXELS
MAP_SIZE_METERS         = cfg.MAP_SIZE_METERS
class SlamDataModel:

    def __init__(self):
        self.x = None
        self.y = None
        self.theta = None
        self.slam_map = None
        self.mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
        self.updated = Signal()

    def set_position(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta
        self.updated.emit()

    def set_map(self, slam_map):
        self.slam_map = slam_map
        self.updated.emit()

