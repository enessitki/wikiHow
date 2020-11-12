import serial
import serial.tools.list_ports
import time
import matplotlib.pyplot as plt
import struct
import math
# https://github.com/Syarujianai/sbgECom/blob/master/doc/Ellipse%E5%9B%BA%E4%BB%B6%E6%89%8B%E5%86%8C.pdf


def get_device():
    tty_list = list(serial.tools.list_ports.comports())
    for tty in tty_list:
        if tty.pid == 24577 and tty.vid == 1027:
            return tty.device

    return None


class Data:
    def __init__(self, _data):
        self.sync1 = _data[0]
        self.sync2 = _data[1]
        self.message_id = _data[2]
        self.message_class = _data[3]
        self.length = _data[4] + _data[5] * 255
        self.payload = _data[6:-3]
        self.crc = _data[-3] * _data[-2] * 255
        self.end = _data[-1]

        # payload
        self.timestamp = self.to_uint(self.payload[0:4])
        self.roll = self.to_int(self.payload[4:8])
        self.pitch = self.to_int(self.payload[8:12])
        self.yaw = self.to_int(self.payload[12:16])
        self.rollDeg = self.roll*180/math.pi
        self.pitchDeg = self.pitch*180/math.pi
        self.yawDeg = self.yaw*180/math.pi
        self.rollAcc = self.to_int(self.payload[16:20])
        self.pitchAcc = self.to_int(self.payload[20:24])
        self.yawAcc = self.to_int(self.payload[24:28])
        self.solutionStatus = self.to_uint(self.payload[28:32])

    @staticmethod
    def to_uint(arr):
        ret = 0
        for n, num in enumerate(arr):
            ret += num*(255**n)

        return ret

    def to_int(self, arr):
        return struct.unpack("f", bytes(arr))[0]
        # val = self.to_uint(arr)
        # N = len(arr)*4
        # limit = (2**(N-1)) - 1
        #
        # if val > limit:
        #     int_val = (2**N - val) * (-1)
        # else:
        #     int_val = val
        #
        # return int_val

    # def __str__(self):


class Parser:
    def __init__(self):
        self.start = [0xFF, 0x5A, 6, 0, 32, 0]
        self.memory = []
        self.state = 0  # 0: idle, 1: start_0, 2: start_1, 3: id, 4: class, 5: length_0, 6: length_1
        self.payload_length = 0
        self.leftover = []

    def add(self, msg):
        self.leftover.extend(msg.copy())
        done = False
        while not done:
            if len(self.leftover) >= 6:
                if self.leftover[0:6] == self.start:
                    length = self.leftover[4] + self.leftover[5] * 255 + 9
                    if length <= len(self.leftover):
                        ret = self.leftover[0:length].copy()
                        del self.leftover[0:length]
                        return ret
                    else:
                        done = True

                else:
                    self.leftover.pop(0)

            else:
                done = True



        return None
    @staticmethod
    def parse_data(_data):
        return Data(_data)
        # _message_id = _data[0]
        # _message_class = _data[1]
        # _length = _data[2]
        # _payload = _data[3:-1]
        # _crc = _data[-1]
        #
        # return _message_id,


imu_dev_dir = get_device()

assert imu_dev_dir is not None

imu_serial = serial.Serial(port=imu_dev_dir, baudrate=115200)
imu_serial.reset_input_buffer()

parser = Parser()

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ts = []
roll_s = []
pitch_s = []
yaw_s = []

max_t0 = 0
while True:
    t0 = time.time()
    if imu_serial.in_waiting > 0:
        # print("------------------------------------")
        raw_msg = [x for x in imu_serial.read(imu_serial.in_waiting)]
        # print("w", raw_msg)
        raw_data = parser.add(raw_msg.copy())
        # print("r", raw_data)

        if raw_data is not None:
            data = parser.parse_data(raw_data)
            # print(data.timestamp, data.rollDeg, data.length)

            t = data.timestamp/1e6
            ts.append(t)
            roll_s.append(data.rollDeg)
            pitch_s.append(data.pitchDeg)
            yaw_s.append(data.yawDeg)
            if len(ts) > 100:
                ts.pop(0)
                roll_s.pop(0)
                pitch_s.pop(0)
                yaw_s.pop(0)

            ax.clear()
            ax.plot(ts, roll_s, "r")
            ax.plot(ts, pitch_s, "g")
            ax.plot(ts, yaw_s, "b")
            # plt.xlim(t - 10, t + 1)
            # plt.scatter(t, data.rollDeg)
            plt.pause(0.001)
    # if time.time() - t0 > 0.0005:
    max_t0 =(time.time() - t0 + max_t0)/2
    print(time.time() - t0 )

    # time.sleep(0.01)
