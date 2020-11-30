import serial
import math
import matplotlib.pyplot as plt
from drawnow import *

#
startHeader = ''
measuredHeader = ''
hexCounter = 0
hexData = ''
hex_list = []
coordinate_x_list = []
coordinate_y_list = []
plt.ion()
plt.style.use('seaborn')

ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=38400,
)

ser.isOpen()


##############################################################################
def find_header(readed_byte):
    global startHeader
    global hexCounter
    startHeader = startHeader + readed_byte
    if '000000000000' in startHeader and 'bbbb1111' in startHeader:
        if len(startHeader) > 51:
            measurement_data_in_telegram = startHeader[0:len(startHeader) - 52]
            if len(measurement_data_in_telegram) == 2164:
                set_coordinate(measurement_data_in_telegram, 80, 110)

        startHeader = ''
        hexCounter = 0
        return True
    else:
        return False


def set_coordinate(data, start_angle, end_angle):
    global hex_list
    x = 0
    y = 0
    n = len(data)
    angle = -45
    # print(N)
    while x < n:
        hex_value = "0x" + data[2 + x] + data[3 + x] + data[0 + x] + data[1 + x]
        int_value = int(hex_value, 16) & 0x1fff
        if start_angle <= angle <= end_angle:
            coordinate_x_list.append(int_value * math.cos(math.radians(angle)))
            coordinate_y_list.append(int_value * math.sin(math.radians(angle)))
        angle += 0.50
        x += 4

    drawnow(plot_values)
    coordinate_x_list.clear()
    coordinate_y_list.clear()
    coordinate_x_list.append(0)
    coordinate_y_list.append(0)


def plot_values():
    plt.plot(coordinate_x_list, coordinate_y_list, linestyle='', marker='o', markersize=2)


###############################################################################


print("connected to: " + ser.portstr)

count = 0
while True:
    for line in ser.read().hex():
        hexCounter += 1
        hexData += line
        if (find_header(line) == True):
            hexData = ''
            print('Data Başladı')

        count = count + 1

ser.close()
