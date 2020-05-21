import time
import pygame
import math
pygame.init()
from AutoPlot import AutoPlot

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

    def is_inside_the_box(self, point):
        x = point[0]
        y = point[1]

        if self.x <= x <= self.x + self.width - 1 and\
            self.y <= y <= self.y + self.height - 1:
            return True
        else:
            return False

    def get_center(self):
        return int(self.x + self.width / 2), int(self.y + self.height / 2)

    def calculate_shifted_center(self, _dx, _dy):
        return int(self.x + _dx + self.width / 2), int(self.y + _dy + self.height / 2)


class Vehicle(StaticBox):
    def __init__(self, x, y, width, height, velocity):
        super().__init__(x, y, width, height, color=(0, 255, 0))
        self.velocity = velocity
        self.initialX = x + int(width/2)
        self.initialY = y + int(height/2)
        self.angle = 0
        self.corners = []
        self.lastMeasurements = []
        self.maxDistance = 1000
        self.sensorRelativePositions = []
        self.sensorRelativeAngles = \
            [
                0, 0, 0,
                90,   90,
                   180,
                -90,   -90,
            ]
            # [
            #     0, 0, 0,
            #     90, 90, 90,
            #     180, 180, 180,
            #     -90, -90, -90,
            # ]

    def move_forward(self, step):
        radian = self.angle / 180 * math.pi
        dx = int(math.cos(radian)*step)
        dy = int(math.sin(radian)*step)
        self.x += dx
        self.y += dy
        return dx, dy

    def calculate_corners(self):
        vehicle_center = self.get_center()
        p0 = (self.x + self.width - 1, self.y)
        p1 = (self.x + self.width - 1, self.y + self.height - 1)
        p2 = (self.x, self.y + self.height - 1)
        p3 = (self.x, self.y)
        self.angle %= 360
        radian = -self.angle / 180 * math.pi

        p0 = self.rotate_around_point(p0, radian, origin=vehicle_center)
        p1 = self.rotate_around_point(p1, radian, origin=vehicle_center)
        p2 = self.rotate_around_point(p2, radian, origin=vehicle_center)
        p3 = self.rotate_around_point(p3, radian, origin=vehicle_center)

        self.corners = [p0, p1, p2, p3]

    def draw_distance_sensor(self, p0, angle):
        radian = angle/180*math.pi
        unit_x = math.cos(radian)
        unit_y = math.sin(radian)
        x0, y0 = p0
        x1 = x0
        y1 = y0
        is_done = False
        while not is_done:
            if x1 >= screen_width or y1 >= screen_height or x1 <= 0 or y1 <= 0:
                is_done = True
            elif win.get_at((int(x1), int(y1))) == (100, 100, 100, 255):
                is_done = True
            else:
                x1 += unit_x
                y1 += unit_y

        pygame.draw.line(win, (255, 0, 0), (int(x0), int(y0)), (int(x1), int(y1)), 2)

        d = ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** (1 / 2)
        return d if d <= self.maxDistance else 1100

    def draw_me(self):
        vehicle_center = self.get_center()
        p0 = self.corners[0]
        p1 = self.corners[1]
        p2 = self.corners[2]
        p3 = self.corners[3]

        pygame.draw.line(win, (0, 255, 0), p0, p1, 2)
        pygame.draw.line(win, (255, 0, 0), p1, p2, 2)
        pygame.draw.line(win, (255, 0, 0), p2, p3, 2)
        pygame.draw.line(win, (255, 0, 0), p3, p0, 2)

        self.sensorRelativePositions = \
            [
                self.sub(p0, vehicle_center), self.sub(self.mean(p0, p1), vehicle_center), self.sub(p1, vehicle_center),
                self.sub(p1, vehicle_center),                                              self.sub(p2, vehicle_center),
                                              self.sub(self.mean(p2, p3), vehicle_center),
                self.sub(p3, vehicle_center),                                              self.sub(p0, vehicle_center),
            ]
            # [
            #     self.sub(p0, vehicle_center), self.sub(self.mean(p0, p1), vehicle_center), self.sub(p1, vehicle_center),
            #     self.sub(p1, vehicle_center), self.sub(self.mean(p1, p2), vehicle_center), self.sub(p2, vehicle_center),
            #     self.sub(p2, vehicle_center), self.sub(self.mean(p2, p3), vehicle_center), self.sub(p3, vehicle_center),
            #     self.sub(p3, vehicle_center), self.sub(self.mean(p3, p0), vehicle_center), self.sub(p0, vehicle_center),
            # ]

        self.lastMeasurements = []
        for pnt, angle in zip(self.sensorRelativePositions, self.sensorRelativeAngles):
            d = self.draw_distance_sensor(self.sum(pnt, vehicle_center), self.angle + angle)
            self.lastMeasurements.append(d)

    def redraw(self):
        vehicle_center = self.get_center()
        p0 = self.corners[0]
        p1 = self.corners[1]
        p2 = self.corners[2]
        p3 = self.corners[3]

        pygame.draw.line(win, (0, 255, 0), p0, p1, 2)
        pygame.draw.line(win, (255, 0, 0), p1, p2, 2)
        pygame.draw.line(win, (255, 0, 0), p2, p3, 2)
        pygame.draw.line(win, (255, 0, 0), p3, p0, 2)
        for pnt, angle in zip(self.sensorRelativePositions, self.sensorRelativeAngles):
            d = self.draw_distance_sensor(self.sum(pnt, vehicle_center), self.angle + angle)

    @staticmethod
    def mean(p0, p1):
        return (p0[0] + p1[0])/2, (p0[1] + p1[1])/2

    @staticmethod
    def sum(p0, p1):
        return p0[0] + p1[0], p0[1] + p1[1]

    @staticmethod
    def sub(p0, p1):
        return p0[0] - p1[0], p0[1] - p1[1]

    @staticmethod
    def rotate_around_point(xy, radians, origin=(0, 0)):
        x, y = xy
        offset_x, offset_y = origin
        adjusted_x = (x - offset_x)
        adjusted_y = (y - offset_y)
        cos_rad = math.cos(radians)
        sin_rad = math.sin(radians)
        qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
        qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y

        return int(qx), int(qy)


staticBoxes = [StaticBox(x=0, y=0, width=100, height=100),
               StaticBox(x=400, y=0, width=100, height=100),
               # StaticBox(x=200, y=200, width=100, height=100),
               # StaticBox(x=600, y=100, width=200, height=600),
               ]

vehicle = Vehicle(x=400, y=350, width=55, height=55, velocity=5)
auto_plot = AutoPlot(vehicle)
run = True
isAutoPlotEnabled = True
while run:
    pygame.time.delay(25)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    else:
        if isAutoPlotEnabled:
            auto_plot.decide_motion()

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
            if keys[pygame.K_r]:
                vehicle.angle += 10

    # draw
    win.fill((255, 255, 255))
    vehicle.calculate_corners()
    for box in staticBoxes:
        box.draw()
        for point in vehicle.corners:
            if box.is_inside_the_box(point):
                print("collision !!!", time.time())
                run = False
    vehicle.draw_me()

    if isAutoPlotEnabled:
        for key in auto_plot.grid:
            xy = [int(a) for a in key.split(",")]
            x = xy[0] * auto_plot.gridSize + vehicle.initialX
            y = xy[1] * auto_plot.gridSize + vehicle.initialY
            w = auto_plot.gridSize
            h = auto_plot.gridSize
            x = int(x - w / 2)
            y = int(y - h / 2)
            if auto_plot.grid[key] == -1:
                pygame.draw.rect(win, (0, 0, 0, 0), (x, y, w, h))
            elif auto_plot.grid[key] == 1:
                pygame.draw.rect(win, (0, 0, 150, 255), (x, y, w, h))
            elif auto_plot.grid[key] == 0:
                pygame.draw.rect(win, (0, 0, 100, 255), (x, y, w, h))

        vehicle.redraw()


    pygame.display.update()

pygame.quit()
