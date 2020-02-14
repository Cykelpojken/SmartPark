from roboviz import MapVisualizer
from car_controller.car_controller_ import CarController
import numpy as np
import config as cfg
import image_processing as ip
import time


MAP_SIZE_PIXELS         = cfg.MAP_SIZE_PIXELS
MAP_SIZE_METERS         = cfg.MAP_SIZE_METERS
MAP_SIZE_PIXELS_1       = 1118
DEFAULT_SLAM_MAP        = False


c = CarController("localhost")
viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM') if DEFAULT_SLAM_MAP else MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_PIXELS_1, MAP_SIZE_METERS, 'SLAM')

while True:
    mapimg = np.reshape(np.frombuffer(c.slam_data_model.mapbytes, dtype=np.uint8), (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS))
    if c.slam_data_model.x is not None:
        #if not viz.display(c.slam_data_model.x/1000., c.slam_data_model.y/1000., 1, c.slam_data_model.mapbytes):
        mapimg = np.reshape(np.frombuffer(c.slam_data_model.mapbytes, dtype=np.uint8), (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS))
        t_map = ip.thresholding(mapimg)
        d_map = ip.dilation(t_map)
        t_e_map =  ip.erosion(d_map)
        blur = ip.blur(t_e_map)
        identified = ip.find_spot(blur)
        identified = identified.copy(order='C')

        if not viz.display(c.slam_data_model.x/1000., c.slam_data_model.y/1000., 1, identified):
            exit(0)
        else:
            time.sleep(0.1)