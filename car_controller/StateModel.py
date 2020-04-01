import collections
import car_controller.signal_protobuf_pb2 as pb
import time

Signal = collections.namedtuple("Signal", ["id", "data", "timestamp"])

class StateModel:
    def __init__(self, signalCount: int):
        self.signals = []
        for i in range(signalCount + 1):
            self.signals.append(Signal(i, None, None))

    def serialize_to_proto(self):
        signaldb_proto = pb.CAN_Signals()
        signaldb_proto.timestamp = time.time()
        for signal in self.signals:
            if signal.timestamp != None and signal.data is not None:
                signal_proto = signaldb_proto.signals.add()
                signal_proto.id = signal.id
                signal_proto.float_data = signal.data
        return signaldb_proto.SerializeToString()
