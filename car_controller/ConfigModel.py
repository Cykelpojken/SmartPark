
class ConfigModel:
    def __init__(self):
        self.address = None
        self.lidar_port  = 5553
        self.can_port    = 5556
        self.camera_port = 5557
        self.lidar_server_address = "192.168.150.154"
        self.use_local_slam = False
