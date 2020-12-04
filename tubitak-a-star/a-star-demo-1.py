"""

A* grid planning

author: Atsushi Sakai(@Atsushi_twi)
        Nikos Kanargias (nkana@tee.gr)

See Wikipedia article (https://en.wikipedia.org/wiki/A*_search_algorithm)

"""

import math

import matplotlib.pyplot as plt

import heapq

import time

show_animation = False


class OpenKey:
    open_set = dict()

    def __init__(self, key, open_set):
        self.key = key
        self.open_set = open_set

    def __lt__(self, other):
        return self.open_set[self.key].f() < self.open_set[other.key].f()

    # @staticmethod
    # def calc_heuristic(n1, n2):
    #     w = 1.0  # weight of heuristic
    #     d = w * math.hypot(n1.x - n2.x, n1.y - n2.y)
    #     return d


class AStarPlanner:

    def __init__(self, ox, oy, resolution, rr):
        """
        Initialize grid map for a star planning

        ox: x position list of Obstacles [m]
        oy: y position list of Obstacles [m]
        resolution: grid resolution [m]
        rr: robot radius[m]
        """

        self.resolution = resolution
        self.rr = rr
        self.min_x, self.min_y = 0, 0
        self.max_x, self.max_y = 0, 0
        self.obstacle_map = None
        self.x_width, self.y_width = 0, 0
        self.motion = self.get_motion_model()
        self.calc_obstacle_map(ox, oy)
        self.open_set = dict()

    class Node:
        def __init__(self, x, y, cost, parent_index, heuristic):
            self.x = x  # index of grid
            self.y = y  # index of grid
            self.cost = cost
            self.heuristic = heuristic
            self.parent_index = parent_index

        def __str__(self):
            return str(self.x) + "," + str(self.y) + "," + str(
                self.cost) + "," + str(self.parent_index)

        def f(self):
            return self.cost + self.heuristic

    def planning(self, sx, sy, gx, gy):
        t0 = time.time()
        """
        A star path search

        input:
            s_x: start x position [m]
            s_y: start y position [m]
            gx: goal x position [m]
            gy: goal y position [m]

        output:
            rx: x position list of the final path
            ry: y position list of the final path
        """

        start_node = self.Node(self.calc_xy_index(sx, self.min_x),
                               self.calc_xy_index(sy, self.min_y), 0.0, -1, 0)
        goal_node = self.Node(self.calc_xy_index(gx, self.min_x),
                              self.calc_xy_index(gy, self.min_y), 0.0, -1, 0)

        self.open_set, closed_set = dict(), dict()
        open_list = []
        heapq.heapify(open_list)
        self.open_set[self.calc_grid_index(start_node)] = start_node
        heapq.heappush(open_list, OpenKey(self.calc_grid_index(start_node), self.open_set))

        while 1:
            if len(self.open_set) == 0:
                print("Open set is empty..")
                break

            # c_id = min(
            #     self.open_set,
            #     key=lambda o: self.open_set[o].cost + self.calc_heuristic(goal_node,
            #                                                          self.open_set[
            #                                                              o]))

            c_id = heapq.heappop(open_list).key

            current = self.open_set[c_id]

            # show graph
            if show_animation:  # pragma: no cover
                plt.plot(self.calc_grid_position(current.x, self.min_x),
                         self.calc_grid_position(current.y, self.min_y), "xc")
                # for stopping simulation with the esc key.
                plt.gcf().canvas.mpl_connect('key_release_event',
                                             lambda event: [exit(
                                                 0) if event.key == 'escape' else None])
                if len(closed_set.keys()) % 10 == 0:
                    plt.pause(0.001)

            if current.x == goal_node.x and current.y == goal_node.y:
                print("Find goal")
                goal_node.parent_index = current.parent_index
                goal_node.cost = current.cost
                break

            # Remove the item from the open set
            del self.open_set[c_id]

            # Add it to the closed set
            closed_set[c_id] = current

            # expand_grid search grid based on motion model
            for i, _ in enumerate(self.motion):
                node = self.Node(current.x + self.motion[i][0],
                                 current.y + self.motion[i][1],
                                 current.cost + self.motion[i][2], c_id,
                                 self.calc_heuristic2(current.x + self.motion[i][0],
                                                      current.y + self.motion[i][1], goal_node.x, goal_node.y))
                n_id = self.calc_grid_index(node)

                # If the node is not safe, do nothing
                if not self.verify_node(node):
                    continue

                if n_id in closed_set:
                    continue

                if n_id not in self.open_set:
                    self.open_set[n_id] = node  # discovered a new node
                    heapq.heappush(open_list, OpenKey(self.calc_grid_index(node), self.open_set))

                else:
                    if self.open_set[n_id].cost > node.cost:
                        # This path is the best until now. record it
                        self.open_set[n_id] = node

        rx, ry = self.calc_final_path(goal_node, closed_set)
        print("time:", time.time() - t0)

        return rx, ry

    def calc_final_path(self, goal_node, closed_set):
        # generate final course
        rx, ry = [self.calc_grid_position(goal_node.x, self.min_x)], [
            self.calc_grid_position(goal_node.y, self.min_y)]
        parent_index = goal_node.parent_index
        while parent_index != -1:
            n = closed_set[parent_index]
            rx.append(self.calc_grid_position(n.x, self.min_x))
            ry.append(self.calc_grid_position(n.y, self.min_y))
            parent_index = n.parent_index

        return rx, ry

    @staticmethod
    def calc_heuristic(n1, n2):
        w = 1.0  # weight of heuristic
        d = w * math.hypot(n1.x - n2.x, n1.y - n2.y)
        return d

    @staticmethod
    def calc_heuristic2(x0, y0, x1, y1):
        w = 1.0  # weight of heuristic
        d = w * math.hypot(x0 - x1, y0 - y1)
        return d

    def calc_grid_position(self, index, min_position):
        """
        calc grid position

        :param index:
        :param min_position:
        :return:
        """
        pos = index * self.resolution + min_position
        return pos

    def calc_xy_index(self, position, min_pos):
        return round((position - min_pos) / self.resolution)

    def calc_grid_index(self, node):
        return (node.y - self.min_y) * self.x_width + (node.x - self.min_x)

    def verify_node(self, node):
        px = self.calc_grid_position(node.x, self.min_x)
        py = self.calc_grid_position(node.y, self.min_y)

        if px < self.min_x:
            return False
        elif py < self.min_y:
            return False
        elif px >= self.max_x:
            return False
        elif py >= self.max_y:
            return False

        # collision check
        if self.obstacle_map[node.x][node.y]:
            return False

        return True

    def calc_obstacle_map(self, ox, oy):

        self.min_x = round(min(ox))
        self.min_y = round(min(oy))
        self.max_x = round(max(ox))
        self.max_y = round(max(oy))
        print("min_x:", self.min_x)
        print("min_y:", self.min_y)
        print("max_x:", self.max_x)
        print("max_y:", self.max_y)

        self.x_width = round((self.max_x - self.min_x) / self.resolution)
        self.y_width = round((self.max_y - self.min_y) / self.resolution)
        print("x_width:", self.x_width)
        print("y_width:", self.y_width)

        # obstacle map generation
        self.obstacle_map = [[False for _ in range(self.y_width)]
                             for _ in range(self.x_width)]
        for ix in range(self.x_width):
            x = self.calc_grid_position(ix, self.min_x)
            for iy in range(self.y_width):
                y = self.calc_grid_position(iy, self.min_y)
                for iox, ioy in zip(ox, oy):
                    d = math.hypot(iox - x, ioy - y)
                    if d <= self.rr:
                        self.obstacle_map[ix][iy] = True
                        break

    @staticmethod
    def get_motion_model():
        # dx, dy, cost
        motion = [[1, 0, 1],
                  [0, 1, 1],
                  [-1, 0, 1],
                  [0, -1, 1],
                  [-1, -1, math.sqrt(2)],
                  [-1, 1, math.sqrt(2)],
                  [1, -1, math.sqrt(2)],
                  [1, 1, math.sqrt(2)]]

        return motion


def main():
    print(__file__ + " start!!")

    # start and goal position
    sx = 10.0  # [m]
    sy = 10.0  # [m]
    gx = 50.0  # [m]
    gy = 50.0  # [m]
    grid_size = 2.0  # [m]
    robot_radius = 1.0  # [m]

    # set obstacle positions
    ox, oy = [], []
    for i in range(-10, 60):
        ox.append(i)
        oy.append(-10.0)
    for i in range(-10, 60):
        ox.append(60.0)
        oy.append(i)
    for i in range(-10, 61):
        ox.append(i)
        oy.append(60.0)
    for i in range(-10, 61):
        ox.append(-10.0)
        oy.append(i)
    for i in range(-10, 40):
        ox.append(20.0)
        oy.append(i)
    for i in range(0, 40):
        ox.append(40.0)
        oy.append(60.0 - i)

    if show_animation:  # pragma: no cover
        plt.plot(ox, oy, ".k")
        plt.plot(sx, sy, "og")
        plt.plot(gx, gy, "xb")
        plt.grid(True)
        plt.axis("equal")

    a_star = AStarPlanner(ox, oy, grid_size, robot_radius)
    rx, ry = a_star.planning(sx, sy, gx, gy)

    if show_animation:  # pragma: no cover
        plt.plot(rx, ry, "-r")
        plt.pause(0.001)
        plt.show()


if __name__ == '__main__':
    main()










# import math
# import matplotlib.pyplot as plt
# import heapq
#
#
# class AStar:
#     def __init__(self, grid_size):
#         self.gridSize = grid_size
#         self.motion = self.get_motion_model()
#
#     @staticmethod
#     def get_distance_of(p0, p1):
#         return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
#
#     @staticmethod
#     def convert_to_id(p):
#         return str(p[0]) + "," + str(p[1])
#
#     @staticmethod
#     def convert_to_point(_id):
#         return [int(x) for x in _id.split(",")]
#
#     def quantize(self, arr):
#         if type(arr) == list:
#             return [int(x)/self.gridSize if not type(x) == list else [int(y)/self.gridSize for y in x] for x in arr]
#         else:
#             return int(arr / self.gridSize)
#
#     @staticmethod
#     def get_motion_model():
#         # dx, dy, cost
#         motion = [[1, 0, 1],
#                   [0, 1, 1],
#                   [-1, 0, 1],
#                   [0, -1, 1],
#                   [-1, -1, math.sqrt(2)],
#                   [-1, 1, math.sqrt(2)],
#                   [1, -1, math.sqrt(2)],
#                   [1, 1, math.sqrt(2)]]
#
#         return motion
#
#     def calc_final_path(self, goal_node, closed_set):
#         ret = [goal_node.point]
#         _next = goal_node.parent_id
#         while True:
#             if _next == -1:
#                 break
#             node = closed_set[_next]
#             ret.append(node.point)
#             _next = node.parent_id
#
#         return ret
#
#     def plan(self, s, g, obstacles):
#         # quantization
#         s = self.quantize(s)
#         g = self.quantize(g)
#         obstacles = self.quantize(obstacles)
#
#         # define open set
#         open_set = []
#         open_hash = {}
#         heapq.heapify(open_set)
#
#         # define close set
#         closed_set = {}
#
#         # define s and g node
#         goal_node = Node(g, 0, self.convert_to_id(s), None, None)
#         start_node = Node(s, 0, self.convert_to_id(s), None, goal_node)
#
#         # add start node to open_set
#         heapq.heappush(open_set, start_node)
#         open_hash[start_node.id] = start_node
#
#         while True:
#             if len(open_set) == 0:
#                 print("Open set is empty..")
#                 break
#
#             current = heapq.heappop(open_set)
#             del open_hash[current.id]
#
#             if current == goal_node:
#                 print("Find goal")
#                 goal_node.parent_index = current.parent_id
#                 goal_node.cost = current.cost
#                 break
#
#             # Add it to the closed set
#             closed_set[current.id] = current
#
#             # expand_grid search grid based on motion model
#             for i, _ in enumerate(self.motion):
#                 p = [current.point[0] + self.motion[i][0],
#                      current.point[1] + self.motion[i][1]]
#
#                 node = Node(p, current.cost + self.motion[i][2],
#                             self.convert_to_id(p), current.id, goal_node)
#
#                 n_id = node.id
#
#                 # If the node is not safe, do nothing
#                 if node.point in obstacles:
#                     continue
#
#                 if n_id in closed_set:
#                     continue
#
#                 if n_id not in open_hash:
#                     # open_set[n_id] = node  # discovered a new node
#                     heapq.heappush(open_set, node)
#                     open_hash[node.id] = node
#                 else:
#                     if open_hash[n_id].cost > node.cost:
#                         # This path is the best until now. record it
#                         open_hash[n_id] = node
#
#         rx, ry = self.calc_final_path(goal_node, closed_set)
#
#         return rx, ry
#
#
# class Node:
#     def __init__(self, p, cost, _id, parent_id, goal_node):
#         self.point = p
#         self.cost = cost
#         self.id = _id
#         self.parent_id = parent_id
#         p0 = p
#         if goal_node is None:
#             p1 = p
#         else:
#             p1 = goal_node.point
#
#         self.hCost = math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
#
#     def __lt__(self, other):
#         return (self.cost + self.hCost) < (other.cost + other.hCost)
#
#     def __eq__(self, other):
#         return self.point == other.point
#
#
#
# def a_star(sx, sy, gx, gy, ox, oy, grid_size):
#     pass
#
#
# def main():
#     grid_size = 0.1
#     o = \
#         [
#             [1, 1],
#             [2, 2],
#             [3, 3]
#         ]
#
#     s = [0, 0]
#     g = [10, 10]
#
#     a = AStar(grid_size=grid_size)
#
#     ret = a.plan(s, g, o)
#
#     # for n in range(len(ret)):
#     #     print(he)
#
#
# if __name__ == '__main__':
#     main()
