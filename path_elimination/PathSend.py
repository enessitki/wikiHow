import socket
import serial
import math


class path_elimination:
    def __init__(self):
        pass
        #self.coordinates = []

    def cal_dist(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return dist

    def min_dist(self, point1, point2):
        dist = path_elimination.calDist(point1, point2)
        if dist < 2.5:
            return False
        else:
            return True

    def max_dist(self, point1, point2):
        dist = path_elimination.calDist(point1, point2)
        if dist > 20:
            return False
        else:
            return True

    def min_angle(self, point1, point2, point3):
        angle = path_elimination.calAngle(point1, point2, point3)
        if angle > 10:  # little sharp angle
            return True
        else:
            return False

    def max_angle(self, point1, point2, point3):
        angle = path_elimination.calAngle(point1, point2, point3)
        if angle < 160:  # ignore angle
            return True
        else:
            return False

    def cal_bearing(self,lat1, lat2, lon1, lon2):
        dLon = lon2 - lon1
        y = math.sin(dLon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
        brng = math.atan2(y, x).toDeg()
        if brng < 0: brng += 360
        return brng

    def eliminate_path(self, lat, lon):
        data = (lat, lon)
        self.coordinates = []
        l1 = len(self.coordinates)
        if l1 < 2:
            self.coordinates.append(data)
        else:
            tf_max_dist = path_elimination.max_dist(self, self.coordinates[l1 - 1], data)
            tf_min_dist = path_elimination.min_dist(self, self.coordinates[l1 - 1], data)
            tf_max_ang = path_elimination.max_angle(self, self.coordinates[l1 - 2], self.coordinates[l1 - 1], data)
            tf_min_ang = path_elimination.min_angle(self, self.coordinates[l1 - 2], self.coordinates[l1 - 1], data)
            if tf_max_dist == True:
                if tf_min_dist == True:
                    if tf_max_dist == True:
                        if tf_max_ang == True and tf_min_ang == True:
                            self.coordinates.append(data)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                self.coordinates.append(data)

# converting str to 32bit
def coordinate_str_convert_32(self, coordinate_str):
    int_val = int(float(self.coordinate_str) * 1000000)
    if int_val < 0:
        int_val += 0xffffffff + 1

    bytes_val = [x for x in int_val.to_bytes(4, byteorder="big")]

    return bytes_val

# converting 32bit to integer
def coordinate_32_convert_to_int(self, bytes_val):
    val = bytes_val[0] * 256 * 256 * 256 + bytes_val[1] * 256 * 256 + bytes_val[2] * 256 + bytes_val[3]
    if val > 0x7fffffff:
        int_val = (0xffffffff - val + 1) * (-1)

    else:
        int_val = val

    return int_val / 1000000

localIP = "192.168.2.68"
localPortRead = 6500
localPortSend = 6600
# set up the socket using local address
socketSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketReceive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketReceive.bind(("192.168.1.91", localPortRead))
coords = []
p1 = path_elimination(coords)
while True:
    # get the data sent to us
    data, ip = socketReceive.recvfrom(9)
    data = [x for x in data]

    lat = coordinate_32_convert_to_int(data[0:4])
    lon = coordinate_32_convert_to_int(data[4:8])
    mod = data[8]

    if mod == 0:
        p1.eliminate_path(lat, lon)
    elif mod == 1:
        coords = p1.coordinates
        l2 = len(coords)
        last_lat, last_lon = coords[l2-1]
        bear = path_elimination.cal_bearing(last_lat, last_lat, lon, lon)

        msg = [0] * 9
        socketSend.sendto(serial.to_bytes(msg), (localIP, localPortSend))

    else:
        pass

"""
msg_bytes = []
msg_bytes.append(lat)
msg_bytes.append(lon)
msg_bytes.append(bear)
sock.sendto(msg_bytes, ("192.168.1.100", 6600))
"""



