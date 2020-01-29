from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from car_controller.LidarScanModel import LidarScanModel
from car_controller.SlamDataModel import SlamDataModel

MAP_SIZE_PIXELS         = 2000
MAP_SIZE_METERS         = 50
LIDAR_DEVICE            = '/dev/ttyUSB0'

slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)


previous_distances = None
previous_angles    = None


class SlamController():
    def __init__(self,
                 lidar_scan_model: LidarScanModel,
                 slam_data_model: SlamDataModel):
        self.active = True
        self.lidar_scan_model = lidar_scan_model
        self.slam_data_model = slam_data_model
        self.lidar_scan_model.scan_data_updated.connect(self.update_slam)

    def update_slam(self):
        if self.active:
            distances = [x[2] for x in self.lidar_scan_model.scan_data]
            angles =    [x[1] for x in self.lidar_scan_model.scan_data]
            slam.update(distances, scan_angles_degrees=angles)
            slam.getmap(self.slam_data_model.mapbytes)
            self.slam_data_model.set_position(*slam.getpos())

    def set_active(self, state):
        self.active = state
        
    