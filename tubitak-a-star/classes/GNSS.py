import serial
import serial.tools.list_ports
import pynmea2
import time
import sys

class GNSS:
    def __init__(self):
        pid = 0
        vid = 0
        self.gnssSerialDeviceName = self.get_serial_device_name(425, 5446)
        self.gnssSerialDevice = serial.Serial(
            port=self.gnssSerialDeviceName.device,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0)


    def read_gps_data(self):
        if self.gnssSerialDevice.in_waiting > 0:
            sentences = self.gnssSerialDevice.read(self.gnssSerialDevice.in_waiting)
            p0 = sentences.find(b'$GNGGA')
            if p0 > -1:
                gga = sentences[p0:].split(b"\r\n")[0]
                try:
                    msg_parsed = pynmea2.parse(gga.decode())
                    if hasattr(msg_parsed, "latitude"):
                        lastKnownLocation = [msg_parsed.latitude, msg_parsed.longitude]
                        return lastKnownLocation
                    else:
                        return []
                except pynmea2.ParseError as error:
                    print(error)
                    return []



    @staticmethod
    def get_serial_device_name(pid, vid):
        a_list = list(serial.tools.list_ports.comports())
        for tty in a_list:
            if tty.pid == pid and tty.vid == vid:
                return tty
        return None

