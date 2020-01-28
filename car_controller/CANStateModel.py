from car_controller.Signal import Signal
import car_controller.signal_protobuf_pb2 as proto
class CanSignalModel:
    timestamp = None
    data = None
    def __init__(self):
        self.signal_changed = Signal()

    def set_data(self,  data):
        if data != self.data:
            self.data = data
            self.signal_changed.emit()



class CANStateModel:
    def __init__(self):
        self.signals = {}

    def populate_from_proto(self, proto_data):
        """ Currently only supports int """
        state_proto = proto.CAN_Signals()
        state_proto.ParseFromString(proto_data)
        for signal_proto in state_proto.signals:
            if signal_proto.id not in self.signals:
                self.signals[signal_proto.id] = CanSignalModel()
            self.signals[signal_proto.id].set_data(signal_proto.int_data)

    