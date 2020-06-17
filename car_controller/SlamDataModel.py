from car_controller.Signal import Signal
MAP_SIZE_PIXELS         = 500
MAP_SIZE_METERS         = 10
class SlamDataModel:

    def __init__(self):
        self.x = None
        self.y = None
        self.theta = None
        self.slam_map = None
        self.width = 0
        self.height = 0
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

    def set_map_dimentions(self, height, width):
        self.width = width
        self.height = height
