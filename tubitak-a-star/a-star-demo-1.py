import math
import matplotlib.pyplot as plt
import heapq


class AStar:
    def __init__(self, grid_size):
        self.gridSize = grid_size
        self.motion = self.get_motion_model()

    @staticmethod
    def get_distance_of(p0, p1):
        return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

    @staticmethod
    def convert_to_id(p):
        return str(p[0]) + "," + str(p[1])

    @staticmethod
    def convert_to_point(_id):
        return [int(x) for x in _id.split(",")]

    def quantize(self, arr):
        if type(arr) == list:
            return [int(x)/self.gridSize if not type(x) == list else [int(y)/self.gridSize for y in x] for x in arr]
        else:
            return int(arr / self.gridSize)

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

    def calc_final_path(self, goal_node, closed_set):
        ret = [goal_node.point]
        _next = goal_node.parent_id
        while True:
            if _next == -1:
                break
            node = closed_set[_next]
            ret.append(node.point)
            _next = node.parent_id

        return ret

    def plan(self, s, g, obstacles):
        # quantization
        s = self.quantize(s)
        g = self.quantize(g)
        obstacles = self.quantize(obstacles)

        # define open set
        open_set = []
        open_hash = {}
        heapq.heapify(open_set)

        # define close set
        closed_set = {}

        # define s and g node
        goal_node = Node(g, 0, self.convert_to_id(s), None, None)
        start_node = Node(s, 0, self.convert_to_id(s), None, goal_node)

        # add start node to open_set
        heapq.heappush(open_set, start_node)
        open_hash[start_node.id] = start_node

        while True:
            if len(open_set) == 0:
                print("Open set is empty..")
                break

            current = heapq.heappop(open_set)
            del open_hash[current.id]

            if current == goal_node:
                print("Find goal")
                goal_node.parent_index = current.parent_id
                goal_node.cost = current.cost
                break

            # Add it to the closed set
            closed_set[current.id] = current

            # expand_grid search grid based on motion model
            for i, _ in enumerate(self.motion):
                p = [current.point[0] + self.motion[i][0],
                     current.point[1] + self.motion[i][1]]

                node = Node(p, current.cost + self.motion[i][2],
                            self.convert_to_id(p), current.id, goal_node)

                n_id = node.id

                # If the node is not safe, do nothing
                if node.point in obstacles:
                    continue

                if n_id in closed_set:
                    continue

                if n_id not in open_hash:
                    # open_set[n_id] = node  # discovered a new node
                    heapq.heappush(open_set, node)
                    open_hash[node.id] = node
                else:
                    if open_hash[n_id].cost > node.cost:
                        # This path is the best until now. record it
                        open_hash[n_id] = node

        rx, ry = self.calc_final_path(goal_node, closed_set)

        return rx, ry


class Node:
    def __init__(self, p, cost, _id, parent_id, goal_node):
        self.point = p
        self.cost = cost
        self.id = _id
        self.parent_id = parent_id
        p0 = p
        if goal_node is None:
            p1 = p
        else:
            p1 = goal_node.point

        self.hCost = math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

    def __lt__(self, other):
        return (self.cost + self.hCost) < (other.cost + other.hCost)

    def __eq__(self, other):
        return self.point == other.point



def a_star(sx, sy, gx, gy, ox, oy, grid_size):
    pass


def main():
    grid_size = 0.1
    o = \
        [
            [1, 1],
            [2, 2],
            [3, 3]
        ]

    s = [0, 0]
    g = [10, 10]

    a = AStar(grid_size=grid_size)

    ret = a.plan(s, g, o)

    # for n in range(len(ret)):
    #     print(he)


if __name__ == '__main__':
    main()
