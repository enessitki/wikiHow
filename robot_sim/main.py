# robot sim
# written by goksel sozeri
import numpy
import time

class Room:
    def __init__(self, width=10, height=5, max_depth=5):
        self.map = numpy.zeros((height + 2, width + 2), dtype=float)
        # build walls
        self.map[0, :] = max_depth
        self.map[-1, :] = max_depth
        self.map[:, 0] = max_depth
        self.map[:, -1] = max_depth
        # self.add_block(1, 1)
        print(self.map)

    def add_block(self, px, py, w=2, h=2, d=1):
        px += 1
        py += 1
        self.map[py: py + w, px: px+h] = d


class DistanceSensor:
    def __init__(self, place, dx, dy, accuracy):
        self.place = place
        self.unitDistance = (dx**2 + dy**2)**(1/2)
        self.dx = dx
        self.dy = dy
        self.accuracy = accuracy

    def measure(self, pos_x, pos_y, room_map):
        pos_x += 1
        pos_y += 1
        done = False
        c = 1
        while not done:
            if room_map[int(pos_y + self.dy * c), int(pos_x + self.dx * c)] > self.place:
                print(c, self.unitDistance)
                return c * self.unitDistance
            c += 1


class Vehicle:
    def __init__(self, width, height, motion_accuracy):
        self.motionAccuracy = motion_accuracy
        self.posX = 0
        self.posY = 0
        self.room = Room()

        self.frontSensor = DistanceSensor(0.5, 0, 1, 0.1)

    def move_to(self, px, py):
        if self.room.map[py + 1, px + 1] == 0:
            self.posX, self.posY = px, py
            print('move_to success', px, py)
            return True
        print('move_to failed', px, py)
        return False

    def motion_logic(self):
        d = self.frontSensor.measure(self.posX, self.posY, self.room.map)
        print(d)
        self.move_to(self.posX + 1, self.posY + 1)

    def apply(self):
        temp_map = self.room.map.copy()
        temp_map[self.posY + 1, self.posX + 1] = -1
        print(temp_map)
        print("motion_logic", time.time())
        self.motion_logic()
        time.sleep(1)


vehicle = Vehicle(1, 1, 0.1)
vehicle.apply()
vehicle.apply()
vehicle.apply()
vehicle.apply()
vehicle.apply()
vehicle.apply()