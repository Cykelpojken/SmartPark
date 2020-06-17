
import pyexcel_ods as px
import struct, pkg_resources

import car_controller.TEM_constants

c = car_controller.TEM_constants.CAN_Gateway_constants()

class Signal_Def():
    """Container class for a single CAN signal definition"""
    def __init__(self, line):
        """
        Constructor fills container from a sheet line.

        line: string array containing each cell's contents as elements
        """
        self.name = line[c.s_name_c]
        self.source = line[c.s_source_c]
        self.source_update = line[c.s_s_upd_c]
        self.source_bus = line[c.s_source_bus_c]
        self.gate_to_prop = line[c.s_g2p_c]
        self.gate_to_safety = line[c.s_g2s_c]
        self.gate_to_info = line[c.s_g2i_c]
        self.data_type = line[c.s_dt_c]
        self.length = line[c.s_len_c]
        self.scaler = line[c.s_scaler_c]
        self.offset = line[c.s_offset_c]
        self.index = line[c.s_sig_idx_c]

    def __str__(self):
        return self.name

class Frame_Def():
    """
    Defines a CAN frame.

    Contains a DLC, transmission period, and a list of signal ids.
    """

    def __init__(self):
        self.dlc = 0
        self.period = 0
        self.signals = []
        self.source_module = None
        self.last_time_send = 0
        self.fast_unpack = False
        self.struct_def = "="
        
    def add_signal(self, signal_id):
        self.signals.append(signal_id)

class CANFramesModel:
    def __init__(self):
        # this_dir,_ = os.path.split(__file__)
        # database_path = os.path.join(this_dir, "signal_database", "signal_database.ods")
        database_path = pkg_resources.resource_filename('car_controller', 'signal_database/signal_database.ods')
        self.database = px.get_data(database_path)
        self.signal_defs = self.load_signals()
        self.frame_defs = self.load_frames()

    def load_signals(self):
        """Load all signals from signal sheet."""
        signal_sheet = self.database["Current Signals"]
        signals = {}
        for line in signal_sheet[2:]:
            idx = line[c.s_sig_idx_c]
            if idx in signals:
                print("Invalid signal index (%s), already defined as <%s>"
                    % (idx, self.signal_defs[idx].name))
                quit()
            signals[idx] = Signal_Def(line)
        return signals

    def load_frames(self):
        """ Load definitions of CAN frames from signal database """
        frame_sheet = self.database["Safety Frames"]
        frame_defs = dict()
        struct_letters = {8:"B", 16: "H"}
        for line in frame_sheet[2:]:
            fid = int(line[c.f_id_c], 16)
            signal = line[c.f_signal_c]
            if fid not in frame_defs:
                frame_defs[fid] = Frame_Def()

            frame_defs[fid].add_signal(signal)
            frame_defs[fid].dlc = line[c.f_dlc_c]
            frame_defs[fid].period = line[c.f_period_c]
            frame_defs[fid].source_module = line[c.f_source_c]

        for frame_id in frame_defs:
            frame = frame_defs[frame_id]
            frame.signals = sorted(frame.signals)
            frame.fast_unpack = True
            for signal_idx in frame.signals:
                signal_d = self.signal_defs[signal_idx]
                if signal_d.length % 8 != 0: # if data is not bytealigned, struct.upcak will not work
                    frame.fast_unpack = False
                    frame.struct_def = ""
                    break
                else:
                    if  signal_d.data_type.lower() == "unsigned":
                        frame.struct_def += struct_letters[signal_d.length]
                    elif signal_d.data_type.lower() == "signed":
                        frame.struct_def += struct_letters[signal_d.length].lower()

            if frame.struct_def != "":
                frame.struct = struct.Struct(frame.struct_def)

                    
        return frame_defs

if __name__ == "__main__":
    c = CANFramesModel()
