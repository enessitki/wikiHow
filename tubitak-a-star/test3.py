"""

A* grid planning

author: Atsushi Sakai(@Atsushi_twi)
        Nikos Kanargias (nkana@tee.gr)

See Wikipedia article (https://en.wikipedia.org/wiki/A*_search_algorithm)

"""

import math

import matplotlib.pyplot as plt
import geopy
from geopy.distance import geodesic

show_animation = True


class AStarPlanner:

    def __init__(self):
        """
        Initialize grid map for a star planning

        ox: x position list of Obstacles [m]
        oy: y position list of Obstacles [m]
        resolution: grid resolution [m]
        rr: robot radius[m]
        """
        self.obstacleList =[]
        self.motion = self.get_motion_model()
        self.index = []
        self.stepSize = 10

    class Node:
        def __init__(self, x, y, cost, parent_index):
            self.x = x  # index of grid
            self.y = y  # index of grid
            self.cost = cost
            self.parent_index = parent_index

        def __str__(self):
            return str(self.x) + "," + str(self.y) + "," + str(
                self.cost) + "," + str(self.parent_index)

    def planning(self, sx, sy, gx, gy):


        start_node = self.Node(x=,y=,cost=0.0, parent_index=-1)
        goal_node = self.Node(x=,y=,cost=0.0, parent_index=-2)

        open_set, closed_set = dict(), dict()
        open_set[self.calc_index(start_node)] = start_node

        while True:
            if len(open_set) == 0:
                print("Open set is empty..")
                break

            # openSet içindeki min fScore değeri bulup seçiyor.
            c_id = min(open_set, key=lambda o: open_set[o].cost + self.calc_heuristic(goal_node, open_set[o]))
            current = open_set[c_id]

            # Goal noktasına gelindi mi
            if current.x == goal_node.x and current.y == goal_node.y:
                print("Find goal")
                goal_node.parent_index = current.parent_index
                goal_node.cost = current.cost
                break

            # Remove the item from the open set
            del open_set[c_id]

            # Add it to the closed set
            closed_set[c_id] = current

            # expand_grid search grid based on motion model
            for i in range(8):  # 8 adet komşu #tek sayılar karenin köşeleri çift sayılar karenin kenarlarının ortası
                neighbor = calc_neighbor(current,i)
                node = self.Node(x=neighbor[0], y=neighbor[1], cost=neighbor[2], parent_index=c_id)
                n_id = self.calc_index(node)

                # If the node is not safe, do nothing
                if not node is in obstacleCircle:
                    continue

                if n_id in closed_set:
                    continue

                if not node is in open_set:
                    open_set[n_id] = node  # discovered a new node
                else:
                    if open_set[n_id].cost > node.cost:
                        # This path is the best until now. record it
                        open_set[n_id] = node

        rx, ry = self.calc_final_path(goal_node, closed_set)

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
        # w = 1.0  # weight of heuristic
        # d = w * math.hypot(n1.x - n2.x, n1.y - n2.y)
        heuristic = geodesic.measure((n1.x, n1.y), (n2.x, n2.y))
        return heuristic

    def calc_index(self, n1):
        return (n1.x, n1.y)







    def calc_neighbor(self,n1,i):
        p1 = geopy.Point(n1.x, n1.y)
        if i%2==0:
            step = self.stepsize
        else:
            step = self.stepsize*1.4

        d = geopy.distance.geodesic(kilometers=step / 1000)
        coord = d.destination(point=p1, bearing=45 * i).format_decimal()
        coord = coord.split(",")
        x = float(coord[0])
        y = float(coord[1])
        cost = n1.cost + step
        return [x, y, cost]






def main():
    print(__file__ + " start!!")

    # start and goal position
    sx = 10.0  # [m]
    sy = 10.0  # [m]
    gx = 50.0  # [m]
    gy = 50.0  # [m]
    grid_size = 2.0  # [m]
    robot_radius = 1.0  # [m]

    rx, ry = a_star.planning(sx, sy, gx, gy)

    if show_animation:  # pragma: no cover
        plt.plot(rx, ry, "-r")
        plt.pause(0.001)
        plt.show()


if __name__ == '__main__':
    main()
