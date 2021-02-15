import adafruit_bno055
import serial
import serial.tools.list_ports





class IMU:
    def __init__(self, ):
        self.serialDevice = self.get_serial_info()
        assert self.serialDevice is not None
        self.serial = serial.Serial(self.serialDevice.device, 38400)
        self.sensor = adafruit_bno055.BNO055_UART(self.serial)

    def get_temperature(self):
        return self.sensor.temperature

    def get_acceleration(self):
        return self.sensor.acceleration

    def get_magnetic(self):
        return self.sensor.magnetic

    def get_gyro(self):
        return self.sensor.gyro

    def get_euler(self):
        return self.sensor.euler

    def get_quaternion(self):
        return self.sensor.quaternion

    def get_linear_acceleration(self):
        return self.sensor.linear_acceleration

    def get_gravity(self):
        return self.sensor.gravity

    def calibration_status(self):
        return self.sensor.calibration_status

    @staticmethod
    def get_serial_info():
        a_list = list(serial.tools.list_ports.comports())
        for tty in a_list:
            if tty.pid == 24577 and tty.vid == 1027:
                return tty
        return None
