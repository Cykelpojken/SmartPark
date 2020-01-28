import car_controller.lidar_proto_pb2 as proto
from car_controller.Signal import Signal

class LidarScanModel:

    def __init__(self):
        self.scan_data = None
        self.timestamp = None
        self.scan_data_updated = Signal()
        
    def populate_from_proto(self, protobuf):
        proto_scan = proto.Scan()
        proto_scan.ParseFromString(protobuf)
        self.timestamp = proto_scan.timestamp
        self.scan_data = [(15, data.angle, data.range) for data in proto_scan.scans]

        self.scan_data_updated.emit()