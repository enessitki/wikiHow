import numpy
import time
import pygame
import math
pygame.init()


screen_width = 1000
screen_height = 500
win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("UV robot Simulator")


class StaticBox:
    def __init__(self, x, y, width, height, color=(100, 100, 100)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))

    def is_collided_with(self, rect):
        if self.x < rect.x + rect.width and \
           self.x + self.width > rect.x and \
           self.y < rect.y + rect.height and \
           self.y + self.height > rect.y:
            return True
        return False

    def get_center(self):
        return int(self.x + self.width / 2), int(self.y + self.height / 2)

    def calculate_shifted_center(self, _dx, _dy):
        return int(self.x + _dx + self.width / 2), int(self.y + _dy + self.height / 2)


class DistanceSensor:
    def __init__(self, _dx, _dy, offset_x, offset_y):
        self.dx = _dx
        self.dy = _dy
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.max_distance = 400

    def draw_from(self, vehicle_box):
        x0, y0 = vehicle_box.get_center()
        x0 += self.offset_x
        y0 += self.offset_y
        x1, y1 = self.measure(vehicle_box)
        pygame.draw.line(win, (255, 0, 0), (x0, y0), (x1, y1), 2)

        return x0, y0, x1, y1, ((x0 - x1)**2 + (y0 - y1)**2)**(1/2)

    def auto_plot_measurement(self, vehicle_box):
        x0, y0 = vehicle_box.get_center()
        x0 += self.offset_x
        y0 += self.offset_y
        x1, y1 = self.measure(vehicle_box)
        d = ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** (1 / 2)
        return d if d <= self.max_distance else 8192

    def measure(self, vehicle_box):
        x0, y0 = vehicle_box.get_center()
        x0 += self.offset_x
        y0 += self.offset_y
        done = False
        count = 0
        while not done:
            x = self.dx * count + x0
            y = self.dy * count + y0
            if not (0 < x < screen_width and 0 < y < screen_height):
                if x < 0:
                    x = 0
                elif x > screen_width:
                    x = screen_width

                if y < 0:
                    y = 0
                elif y > screen_height:
                    y = screen_height

                return x, y

            count += 1
            if win.get_at((x, y)) == (100, 100, 100, 255):
                return x, y


class Vehicle(StaticBox):
    def __init__(self, x, y, width, height, velocity):
        super().__init__(x, y, width, height, color=(0, 255, 0))
        self.velocity = velocity
        self.sensors = [  # r0, r1, r2, d0, d1, d2, l0, l1, l2, u0, u2, u2
                        DistanceSensor(1, 0, round(width / 2) - 1, round(-height / 2) + 1),
                        DistanceSensor(1, 0, round(width/2) - 1, 0),
                        DistanceSensor(1, 0, round(width/2) - 1, round(height/2) - 1),
                        DistanceSensor(0, 1, round(width / 2) - 1, round(height/2) - 1),
                        DistanceSensor(0, 1, 0, round(height/2) - 1),
                        DistanceSensor(0, 1, round(-width / 2) + 1, round(height / 2) - 1),
                        DistanceSensor(-1, 0, round(-width / 2) + 1, round(height / 2) - 1),
                        DistanceSensor(-1, 0, round(-width / 2) + 1, 0),
                        DistanceSensor(-1, 0, round(-width / 2) + 1, round(-height / 2) + 1),
                        DistanceSensor(0, -1, round(-width / 2) + 1, round(-height / 2) + 1),
                        DistanceSensor(0, -1, 0, round(-height / 2) + 1),
                        DistanceSensor(0, -1, round(width / 2) - 1, round(-height / 2) + 1),
                        ]

    def draw_me(self):
        self.draw()
        for k, sensor in enumerate(self.sensors):
            sensor.draw_from(self)


class AutoPlot:
    def __init__(self, center, width=100, height=100):
        self.realCenter = center
        self.width = width
        self.height = height
        self.effectiveRadius = 150
        self.safe_distance = 100
        self.direction = [0, 0]
        self.direction_list = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        self.estimatedPosition = [0, 0]
        # self.estimatedPositionHistory = []
        # self.estimatedPositionHistory.append(self.estimatedPosition)
        self.roomLimits = [-1, 1, -1, 1]
        self.gridTolerance = 0.2
        self.gridSize = 50
        self.map = {}
        # map item
        # len 5
        # [0] -> right edge # -1: blocked, 0: unknown, 1: open
        # [1] -> down edge
        # [2] -> left edge
        # [3] -> up edge
        # [4] -> cell # -1: blocked, 0: undiscovered, 1 discovered

    def calculate_motion(self, measurements):
        # measurements
        r0, r1, r2, d0, d1, d2, l0, l1, l2, u0, u1, u2 = tuple(measurements)
        measured_coords =\
            [
                [self.estimatedPosition[0] + self.width/2 + r0, self.estimatedPosition[1] - self.height/2],
                [self.estimatedPosition[0] + self.width/2 + r1, self.estimatedPosition[1] - 0],
                [self.estimatedPosition[0] + self.width/2 + r2, self.estimatedPosition[1] + self.height/2],
                [self.estimatedPosition[0] + self.width/2, self.estimatedPosition[1] + self.height/2 + d0],
                [self.estimatedPosition[0] + 0           , self.estimatedPosition[1] + self.height/2 + d1],
                [self.estimatedPosition[0] - self.width/2, self.estimatedPosition[1] + self.height/2 + d2],
                [self.estimatedPosition[0] - self.width/2 - l0, self.estimatedPosition[1] + self.height/2],
                [self.estimatedPosition[0] - self.width/2 - l1, self.estimatedPosition[1] - 0],
                [self.estimatedPosition[0] - self.width/2 - l2, self.estimatedPosition[1] - self.height/2],
                [self.estimatedPosition[0] - self.width/2, self.estimatedPosition[1] - self.height/2 - u0],
                [self.estimatedPosition[0] - 0           , self.estimatedPosition[1] - self.height/2 - u1],
                [self.estimatedPosition[0] + self.width/2, self.estimatedPosition[1] - self.height/2 - u2],
            ]
        # update room limits
        self.roomLimits[0] = math.ceil(min(self.roomLimits[0], self.estimatedPosition[0] - self.width/2 - max(l0, l1, l2)))
        self.roomLimits[1] = math.ceil(max(self.roomLimits[1], self.estimatedPosition[0] + self.width/2 + max(r0, r1, r2)))
        self.roomLimits[2] = math.ceil(min(self.roomLimits[2], self.estimatedPosition[1] - self.height/2 - max(u0, u1, u2)))
        self.roomLimits[3] = math.ceil(max(self.roomLimits[3], self.estimatedPosition[1] + self.height/2 + max(d0, d1, d2)))

        # update map
        # arrived grid
        gx = self.estimatedPosition[0] / self.gridSize
        gy = self.estimatedPosition[1] / self.gridSize
        if gx - int(gx) < self.gridTolerance:
            gx = int(gx)
        elif int(gx + 1) - gx < self.gridTolerance:
            gx = int(gx + 1)

        if gy - int(gy) < self.gridTolerance:
            gy = int(gy)
        elif int(gy + 1) - gy < self.gridTolerance:
            gy = int(gy + 1)

        if type(gx) == int and type(gy) == int:
            key = str(gx) + "," + str(gy)
            if key in self.map:
                self.map[key][4] = 1
            else:
                self.map[key] = [0, 0, 0, 0, 1]

        # blocked grid
        for idx, cord in enumerate(measured_coords):
            gmx = cord[0] / self.gridSize
            gmy = cord[1] / self.gridSize
            if gmx - int(gmx) <= 0.5:
                gmx = int(gmx)
            elif int(gmx + 1) - gmx <= 0.5:
                gmx = int(gmx + 1)

            if gmy - int(gmy) <= 0.5:
                gmy = int(gmy)
            elif int(gmy + 1) - gmy <= 0.5:
                gmy = int(gmy + 1)

            if type(gmx) == int and type(gmy) == int:
                key = str(gmx) + "," + str(gmy)
                side_index = int(idx/3)
                if key in self.map:
                    self.map[key][side_index] = -1
                else:
                    arr = [0, 0, 0, 0, 0]
                    arr[side_index] = -1
                    self.map[key] = arr

        # decide next grid
        _dx = self.direction_list[0][0]
        _dy = self.direction_list[0][1]
        self.estimatedPosition[0] += _dx
        self.estimatedPosition[1] += _dy

        # return self.is_safe(measurements)
        return _dx, _dy

    def draw(self):
        for key in self.map.keys():
            coord = [int(x)*self.gridSize for x in key.split(",")]
            coord = [coord[x] + self.realCenter[x] for x in range(2)]
            cell = self.map[key]
            if cell[4] == 1:
                pygame.draw.circle(win, (0, 0, 255), tuple(coord), 10, 2)
            # elif -1 in cell[0:5]:
            for idx, item in enumerate(cell[0:5]):
                if item == -1:
                    if idx == 0:
                        p0 = (coord[0] + int(self.gridSize / 2),
                              coord[1] - int(self.gridSize / 2))
                        p1 = (coord[0] + int(self.gridSize / 2),
                              coord[1] + int(self.gridSize / 2))

                    elif idx == 1:
                        print("here")
                        p0 = (coord[0] + int(self.gridSize / 2),
                              coord[1] + int(self.gridSize / 2))
                        p1 = (coord[0] - int(self.gridSize / 2),
                              coord[1] + int(self.gridSize / 2))

                    elif idx == 2:
                        p0 = (coord[0] - int(self.gridSize / 2),
                              coord[1] + int(self.gridSize / 2))
                        p1 = (coord[0] - int(self.gridSize / 2),
                              coord[1] - int(self.gridSize / 2))
                    else:
                        p0 = (coord[0] - int(self.gridSize / 2),
                              coord[1] + int(self.gridSize / 2))
                        p1 = (coord[0] + int(self.gridSize / 2),
                              coord[1] + int(self.gridSize / 2))

                    pygame.draw.line(win, (0, 0, 0), p0, p1, 2) # 1,0
            # else:
            #     pygame.draw.circle(win, (0, 255, 255), tuple(coord), 10, 2)

    def decide_direction(self, measurements):
        gx = self.estimatedPosition

    def is_safe(self, measurements):
        _dx = 0
        _dy = 0
        for n, m in enumerate(measurements):
            if m < self.safe_distance:
                _dx += self.direction_list[int(n/3)][0] * -1
                _dy += self.direction_list[int(n/3)][1] * -1

        if not _dx == 0:
            _dx = _dx / abs(_dx)

        if not _dy == 0:
            _dy = _dy / abs(_dy)

        return _dx, _dy

    def scan_left_right(self, ml, mr):
        _dx = 0
        _dy = 0
        # if ml > self.effectiveRadius:
        #     _dx = -1
        if self.direction[0] == -1:
            if ml > self.effectiveRadius:
                _dx = -1
            elif mr > self.effectiveRadius:
                _dx = 1
        else:
            if mr > self.effectiveRadius:
                _dx = 1
            elif ml > self.effectiveRadius:
                _dx = -1

        return _dx, _dy

    def toggle_direction(self):
        self.direction = [x*-1 for x in self.direction]


staticBoxes = [StaticBox(x=0, y=0, width=100, height=100),
               StaticBox(x=400, y=0, width=100, height=100),
               # StaticBox(x=200, y=200, width=100, height=100),
               ]

vehicle = Vehicle(x=50, y=100, width=100, height=100, velocity=5)
xc, yc = vehicle.get_center()
print(xc, yc)
autoPlot = AutoPlot([xc, yc], width=100, height=100)
run = True
isAutoPlotEnabled = False
while run:
    pygame.time.delay(25)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    if isAutoPlotEnabled:
        # auto plot
        dx, dy = autoPlot.calculate_motion([x.auto_plot_measurement(vehicle) for x in vehicle.sensors])
        vehicle.x += dx
        vehicle.y += dy

        # wall collision
        if not (0 <= vehicle.x <= screen_width - vehicle.width and
                0 <= vehicle.y <= screen_height - vehicle.height):
            print("collision !!!", time.time())
            run = False

    else:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and vehicle.x >= vehicle.velocity:
            vehicle.x -= vehicle.velocity
        if keys[pygame.K_RIGHT] and vehicle.x <= screen_width - vehicle.width - vehicle.velocity:
            vehicle.x += vehicle.velocity
        if keys[pygame.K_UP] and vehicle.y >= vehicle.velocity:
            vehicle.y -= vehicle.velocity
        if keys[pygame.K_DOWN] and vehicle.y <= screen_height - vehicle.height - vehicle.velocity:
            vehicle.y += vehicle.velocity

    # draw
    win.fill((255, 255, 255))
    for box in staticBoxes:
        box.draw()
        if vehicle.is_collided_with(box):
            print("collision !!!", time.time())
            run = False

    vehicle.draw_me()

    if isAutoPlotEnabled:
        autoPlot.draw()

    pygame.display.update()

pygame.quit()

