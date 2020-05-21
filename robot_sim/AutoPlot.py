import math
from random import randint


class AutoPlot:
    def __init__(self, vehicle):
        self.gridSize = 10
        self.grid = {}
        self.vehicle = vehicle
        self.estimatedPosition = (0, 0)
        self.effectDistance = 150
        self.states = {
                        'discover': {'active': True, 'progress': 0},
                        'search': {'active': False, 'progress': 0},
                        'move': {'active': False, 'progress': 0, 'target': (0, 0)},
                       }
        self.minDistance = 80

    def decide_motion(self):
        # self.estimatedPosition = self.vehicle.get_center()
        self.update_grid()

        if self.states['discover']['active']:
            if self.states['discover']['progress'] < 90:
                self.vehicle.angle += 1
                self.states['discover']['progress'] += 1
            else:
                self.states['discover']['active'] = False
                self.states['discover']['progress'] = 0
                self.states['search']['active'] = True
                self.states['search']['progress'] = 0
        elif self.states['search']['active']:
            min_distance = -1
            min_point = (0, 0)
            p0 = self.estimatedPosition
            p_bonus = (self.effectDistance / 5 * math.cos(self.vehicle.angle / 180 * math.pi),
                       self.effectDistance / 5 * math.sin(self.vehicle.angle / 180 * math.pi))

            for key in self.grid:
                if self.grid[key] == 0:
                    xy = [int(a) for a in key.split(",")]
                    x = xy[0] * self.gridSize
                    y = xy[1] * self.gridSize
                    p1 = (x, y)
                    if min_distance == -1:
                        min_distance = self.l2(p0, p1)
                        min_point = p1
                    else:
                        d = self.l2(p0, self.sub(p1, p_bonus))
                        if min_distance > d:
                            min_distance = d
                            min_point = p1

            if min_distance == -1:
                print("search failed")
                self.states['discover']['active'] = True
                self.states['discover']['progress'] = 0
                self.states['search']['active'] = False
                self.states['search']['progress'] = 0
            else:
                self.states['search']['active'] = False
                self.states['search']['progress'] = 0
                self.states['move']['active'] = True
                self.states['move']['progress'] = 0
                # target_point = self.move_point_to(min_point, p0, self.effectDistance/2)
                self.states['move']['target'] = min_point
        elif self.states['move']['active']:
            p0 = self.estimatedPosition
            p1 = self.states['move']['target']
            if self.get_grid_val(p1) == 0:
                dp = self.collision_control()
                target_angle = self.rotation_angle(p0, p1)
                collision_angle = self.rotation_angle(p0, dp)
                if dp == (0, 0):
                    angle = target_angle
                else:
                    if abs(abs(target_angle - collision_angle) - 180) < 30:
                        print("loop")
                        angle = collision_angle + randint(-20, 20)
                    else:
                        angle = collision_angle
                    # print(target_angle, collision_angle,
                    #       abs((target_angle + collision_angle) % 360 - 180) < 10)
                    # print(abs(abs(target_angle - collision_angle) - 180) )
                    # print(abs(abs(target_angle - collision_angle) - 180) < 30 )

                self.vehicle.angle = angle
                dp = self.vehicle.move_forward(step=self.gridSize)
                self.estimatedPosition = self.sum(self.estimatedPosition, dp)
            else:
                # print("target reached")
                self.states['move']['active'] = False
                self.states['move']['progress'] = 0
                self.states['search']['active'] = True
                self.states['search']['progress'] = 0

    # def line_obstacle_control(self, p0, p1):
    #     angle = self.rotation_angle(p0, p1)
    #     dp = (math.cos(angle / 180 * math.pi) * self.gridSize / 2,
    #           math.sin(angle / 180 * math.pi) * self.gridSize / 2)
    #     is_done = False
    #     p = p0
    #     while not is_done:
    #         if self.l2(self.estimatedPosition, p) <= self.effectDistance:
    #             self.add_point_to_grid(p, 1, rule=[-1])
    #         else:
    #             self.add_point_to_grid(p, 0, rule=[-1, 1])
    #         p = self.sum(p, dp)
    #         if self.l1(p, p1) < self.gridSize:
    #             is_done = True

    def collision_control(self):

        # for n, d in enumerate(self.vehicle.lastMeasurements):
        #     if d <= self.minDistance:
        #         return False
        # return True
        delta = 2 * int(self.minDistance / self.gridSize)
        dp = (0, 0)
        for x in range(delta):
            for y in range(delta):
                xx = (x - int(delta / 2)) * self.gridSize
                yy = (y - int(delta / 2)) * self.gridSize
                if self.l2((xx, yy), (0, 0)) <= self.minDistance:
                    if self.get_grid_val(self.sum(self.estimatedPosition, (xx, yy))) in [-1]:
                        dp = self.sub(dp, (xx, yy))

        return self.norm(dp, self.minDistance)

    def update_grid(self):
        angle = self.vehicle.angle
        for n, d in enumerate(self.vehicle.lastMeasurements):
            # if n not in [4, 6, 8, 10]:
            relative_p0 = self.vehicle.sensorRelativePositions[n]
            relative_angle = self.vehicle.sensorRelativeAngles[n]
            if d > self.vehicle.maxDistance:
                distance = self.vehicle.maxDistance
                is_blocked = False
            else:
                distance = d
                is_blocked = True
            p0 = self.sum(relative_p0, self.estimatedPosition)
            p1 = self.sum(p0, (distance * math.cos((angle + relative_angle)/180*math.pi),
                               distance * math.sin((angle + relative_angle)/180*math.pi)))
            is_done = False
            p = p0
            dp = (math.cos((angle + relative_angle)/180*math.pi) * self.gridSize/2,
                  math.sin((angle + relative_angle)/180*math.pi) * self.gridSize/2)

            # effect_distance = min(self.effectDistance, distance + self.l2(self.estimatedPosition, p0))
            # p2 = self.sum(p0, (effect_distance * math.cos((angle + relative_angle) / 180 * math.pi),
            #                    effect_distance * math.sin((angle + relative_angle) / 180 * math.pi)))

            while not is_done:
                # if self.l2(p0, p) <= effect_distance:
                if self.l2(self.estimatedPosition, p) <= self.effectDistance:
                    self.add_point_to_grid(p, 1, rule=[-1])
                else:
                    self.add_point_to_grid(p, 0, rule=[-1, 1])
                p = self.sum(p, dp)
                if self.l1(p, p1) < self.gridSize:
                    is_done = True

            if is_blocked:
                self.add_point_to_grid(p1, -1)
            else:
                self.add_point_to_grid(p1, 0, rule=[-1, 1])

        p0 = self.estimatedPosition
        delta = 2*int(self.effectDistance / self.gridSize)
        for x in range(delta):
            for y in range(delta):
                xx = (x - int(delta / 2)) * self.gridSize
                yy = (y - int(delta / 2)) * self.gridSize
                # print("here", xx, yy)
                if self.l2((xx, yy), (0, 0)) <= self.effectDistance:
                    self.add_point_to_grid(self.sum(p0, (xx, yy)), 1, rule=[-1])

    def add_point_to_grid(self, point, value, rule=None):
        x, y = point
        x = int(round(x / self.gridSize))
        y = int(round(y / self.gridSize))
        key = str(x) + ',' + str(y)
        if rule is None:
            self.grid[key] = value
        else:
            if key not in self.grid:
                self.grid[key] = value
            else:
                if not self.grid[key] in rule:
                    self.grid[key] = value

    def get_grid_cord(self, point):
        x, y = point
        x = int(round(x / self.gridSize))
        y = int(round(y / self.gridSize))
        return x, y

    def get_grid_val(self, point):
        x, y = point
        x = int(round(x / self.gridSize))
        y = int(round(y / self.gridSize))
        return self.grid[str(x) + ',' + str(y)]

    @staticmethod
    def move_point(p0, angle, step):
        return p0[0] + math.cos(angle/180*math.pi) * step, \
               p0[1] + math.sin(angle/180*math.pi) * step

    @staticmethod
    def move_point_to(p0, p1, step):
        d = ((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)**(1/2)
        r = step / d
        return p0[0] + (p1[0] - p0[0]) * r, p0[1] + (p1[1] - p0[1]) * r

    @staticmethod
    def mean(p0, p1):
        return (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2

    @staticmethod
    def sum(p0, p1):
        return p0[0] + p1[0], p0[1] + p1[1]

    @staticmethod
    def sub(p0, p1):
        return p0[0] - p1[0], p0[1] - p1[1]

    @staticmethod
    def mul(p0, r):
        return p0[0] * r, p0[1] * r

    @staticmethod
    def norm(p0, r=1):
        d = (p0[0] ** 2 + p0[1] ** 2) ** (1 / 2)
        if p0 == (0, 0):
            return 0, 0
        elif p0[0] == 0:
            return 0, p0[1] * r / abs(p0[1])
        elif p0[1] == 0:
            return p0[0] * r / abs(p0[0]), 0

        return p0[0] * r / d, p0[1] * r / d

    @staticmethod
    def l1(p0, p1):
        return abs(p0[0] - p1[0]) + abs(p0[1] - p1[1])

    @staticmethod
    def l2(p0, p1):
        return ((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)**(1/2)

    @staticmethod
    def rotation_angle(p0, p1):
        qx = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        qx = qx /math.pi * 180
        # if p0[1] > p1[1]:
        #     qx = 180 - qx
        #     qx *= -1
        # print(qx)

        return qx
