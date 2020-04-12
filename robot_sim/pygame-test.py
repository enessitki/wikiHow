import numpy
import time
import pygame
pygame.init()


screen_width = 500
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
    def __init__(self, _dx, _dy):
        self.dx = _dx
        self.dy = _dy

    def draw_from(self, vehicle_box):
        x0, y0 = vehicle_box.get_center()
        x1, y1 = self.measure(vehicle_box)
        pygame.draw.line(win, (255, 0, 0), (x0, y0), (x1, y1), 2)

        return x0, y0, x1, y1, ((x0 - x1)**2 + (y0 - y1)**2)**(1/2)

    def auto_plot_measurement(self, vehicle_box):
        x0, y0 = vehicle_box.get_center()
        x1, y1 = self.measure(vehicle_box)
        return ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** (1 / 2)

    def measure(self, vehicle_box):
        x0, y0 = vehicle_box.get_center()
        done = False
        count = int(min(vehicle_box.width, vehicle_box.height) / 2)
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
        self.sensors = [DistanceSensor(1, 0),  # 0,45, 90, 135, 180, 225, 270, 315, 360
                        DistanceSensor(1, 1),
                        DistanceSensor(0, 1),
                        DistanceSensor(-1, 1),
                        DistanceSensor(-1, 0),
                        DistanceSensor(-1, -1),
                        DistanceSensor(0, -1),
                        DistanceSensor(1, -1),
                        ]

    def draw_me(self):
        self.draw()
        for k, sensor in enumerate(self.sensors):
            sensor.draw_from(self)


class AutoPlot:
    def __init__(self, effective_radius):
        self.effectiveRadius = effective_radius
        self.direction = [0, 0]
        # self.map =

    def calculate_motion(self, measurements):
        mr, mrd, md, mld, ml, mlu, mu, mru = tuple(measurements)
        mr -= 50
        md -= 50
        ml -= 50
        mu -= 50

        mru -= 50*pow(2, 1/2)
        mrd -= 50*pow(2, 1/2)
        mlu -= 50*pow(2, 1/2)
        mld -= 50*pow(2, 1/2)

        # _dx, _dy = self.scan_left_right(ml, mr)
        _dx, _dy = self.scan_left_right(mr, mrd)
        print(mr, ml)
        self.direction = [_dx, _dy]
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

vehicle = Vehicle(x=100, y=100, width=100, height=100, velocity=5)
autoPlot = AutoPlot(10)
run = True
isAutoPlotEnabled = True
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
        print(vehicle.x, vehicle.y)

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

    pygame.display.update()

pygame.quit()

