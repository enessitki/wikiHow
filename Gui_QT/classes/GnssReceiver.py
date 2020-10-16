import serial
import serial.tools.list_ports
import pynmea2
from threading import Thread
import sys


class GnssReceiver:
    def __init__(self):
        self.vehicleLastKnownLocation = None
        self.obstacleGeaCoordinateList = None
        self.loopForReadGnssData = Thread(target=self.read_gps_data)
        self.loopForReadGnssData.daemon = True
        self.gnssSerialDevice = None
        self.vehicleLastKnowLocation = None
        self.isInitSuccess = False
        self._OnLocationParsed = None
        self.init()

    def connect_on_location_parsed(self, fn):
        self._OnLocationParsed = fn

    def init(self):
        device = self.scan_ports()
        assert device is not None

        try:
            self.gnssSerialDevice = serial.Serial(
                port=device,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=0)

            if self.gnssSerialDevice.isOpen():
                self.loopForReadGnssData.start()

            self.isInitSuccess = True

        except NameError as e:
            print(e)
        except OSError as e:
            print(e)
        except TypeError as e:
            print(e)
        except:
            print("Unexpected error:", sys.exc_info()[0])

    @staticmethod
    def scan_ports():
        a_list = list(serial.tools.list_ports.comports())
        for tty in a_list:
            if tty.pid == 1282 and tty.vid == 5446:
                return tty.device
        return None

    def read_gps_data(self):
        while True:
            if self.gnssSerialDevice.in_waiting > 0:
                sentences = self.gnssSerialDevice.read(self.gnssSerialDevice.in_waiting)
                p0 = sentences.find(b'$GNGGA')
                if p0 > -1:
                    gga = sentences[p0:].split(b"\r\n")[0]
                    print(gga)
                    try:
                        msg_parsed = pynmea2.parse(gga.decode())
                        if hasattr(msg_parsed, "latitude"):
                            location = [msg_parsed.latitude, msg_parsed.longitude]
                            # print(self.vehicleLastKnownLocation)
                            if not self.vehicleLastKnowLocation == location:
                                self.vehicleLastKnowLocation = location
                                if self._OnLocationParsed is not None:
                                    self._OnLocationParsed(self.vehicleLastKnowLocation)

                    except pynmea2.ParseError as error:
                        print(error)