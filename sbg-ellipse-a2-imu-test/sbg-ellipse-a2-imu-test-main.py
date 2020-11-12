import serial
import serial.tools.list_ports
import time
# https://github.com/Syarujianai/sbgECom/blob/master/doc/Ellipse%E5%9B%BA%E4%BB%B6%E6%89%8B%E5%86%8C.pdf


def get_device():
    tty_list = list(serial.tools.list_ports.comports())
    for tty in tty_list:
        if tty.pid == 24577 and tty.vid == 1027:
            return tty.device

    return None


class Data:
    def __init__(self, _data):
        self.message_id = _data[0]
        self.message_class = _data[1]
        self.length = _data[2] + _data[3] * 255
        self.payload = _data[4:-3]
        self.crc = _data[-3] * _data[-2] * 255
        self.end = _data[-1]

    # def __str__(self):



class Parser:
    def __init__(self):
        self.start = [0xFF, 0x5A]
        self.end = [0x33]
        self.memory = []
        self.state = 0  # 0: idle, 1: start_0, 2: start_1, 3: id, 4: class, 5: length_0, 6: length_1
        self.payload_length = 0
        self.leftover = []

    def add(self, msg):
        start_index = None
        print("s0", self.state)
        print("m0", self.memory)
        self.leftover.extend(msg)
        msg = self.leftover.copy()
        self.leftover = []
        if self.state < 2:
            self.memory = []
            start_index = 0
            for word in msg:
                # print(word, self.state == 0, word == self.start[0])
                if self.state == 0 and word == self.start[0]:
                    self.state = 1
                    print(self.state)

                elif self.state == 1 and word == self.start[1]:
                    self.state = 2
                    print(self.state)
                    break
                elif self.state == 1 and not word == self.start[1]:
                    self.state = 0
                start_index += 1

        if self.state == 2:
            if start_index is not None:
                # print("1", msg)
                if start_index > 0:
                    del msg[0:start_index + 1]
                else:
                    del msg[start_index]
                # print("2", msg)

            if len(msg) > 1:
                self.state = 3
                print(self.state)
                self.memory = []
                self.memory.append(msg[0]) # id
                del msg[0]

        if self.state == 3:
            if len(msg) > 1:
                self.state = 4
                print(self.state)
                self.memory.append(msg[0]) # class
                del msg[0]

        if self.state == 4:
            if len(msg) > 1:
                self.state = 5
                print(self.state)
                self.memory.append(msg[0]) # length 0
                del msg[0]

        if self.state == 5:
            if len(msg) > 1:
                self.state = 6
                print(self.state)
                self.memory.append(msg[0])  # length 1
                del msg[0]
        # print("memory", self.memory)
        if self.state == 6:
            msg_len = len(msg)
            payload_len = self.memory[2] + self.memory[3] * 255
            mem_len = len(self.memory)

            needed_len = payload_len + 7 - mem_len

            print(needed_len, mem_len, msg_len)

            if needed_len == 0:
                self.state = 0
                # self.add(msg)
                print("m", self.memory)
                self.leftover = msg
                return self.memory

            if msg_len < needed_len:
                self.memory.extend(msg)
                print("m", self.memory)

            elif msg_len == needed_len:
                self.memory.extend(msg)
                self.state = 0
                print("m", self.memory)
                return self.memory

            elif msg_len > needed_len:
                self.memory.extend(msg[0:needed_len])
                del msg[0:needed_len]
                self.leftover = msg
                self.state = 0
                print("m", self.memory)
                return self.memory


            # self.payload_length = msg[2]*255 + msg[1]
            # print(self.payload_length)
            # self.memory += [word]
            # for word in msg:
            #     if word == self.end[0]:
            #         self.state = 0
            #         return self.memory
            #     else:
            #         self.memory += [word]

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


while True:
    if imu_serial.in_waiting > 0:
        print("------------------------------------")
        raw_msg = [x for x in imu_serial.read(imu_serial.in_waiting)]
        print("w", raw_msg)
        raw_data = parser.add(raw_msg.copy())
        print("r", raw_data)

        if raw_data is not None:
            data = parser.parse_data(raw_data)
            # print(data.message_id, data.message_class, data.length)

    time.sleep(0.01)
# [28, 245, 186, 88, 72, 132, 187, 171, 220, 51, 255, 90, 7, 0, 36, 0, 104, 96, 111, 58, 185, 222, 127, 191, 225, 183, 194, 56, 208, 96, 2, 189, 191, 188, 190, 186, 38, 102, 0, 59, 223, 42, 0, 59, 241, 217, 24, 62, 18, 1, 0, 0, 128, 219, 51, 255, 90, 3, 0, 58, 0]
