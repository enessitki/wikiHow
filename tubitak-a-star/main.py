import math
import numpy as np
import sys
import time
# import pynmea2
# import serial
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget
from pyqtlet import L, MapWidget
import geopy
from geopy.distance import geodesic
from geographiclib.geodesic import Geodesic
from shapely.geometry import Point, Polygon


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)
        self.setWindowTitle("Title")
        # self.timer = QTimer()
        # self.timer.setInterval(1000)
        # self.timer.timeout.connect(self.read_gps_data)
        # self.timer.start()

        self.buttonMode = ""
        self.colorNumber = 0
        self.colorCodes = ["#FF0000", "#FFC900", "#8FFF00", "#00FF3A", "#00FFC5", "#00B2FF", "#0049FF", "#8F00FF",
                           "#2A7C7A", "#606120", "#3E6632"]
        self.timeStart = None
        self.timePathFin = None
        self.timeDrawFin = None

        self.startMarker = None
        self.goalMarker = None
        self.current_marker = None

        self.start_node = None
        self.goal_node = None
        self.open_set, self.closed_set = dict(), dict()
        self.obstacleList = []

        self.stepSize = 3
        self.obstacleRadius = 10
        self.motion = self.get_motion_model(self.stepSize)

        self.geodesic = geodesic()

        self.mapWidget = MapWidget()
        self.map = L.map(self.mapWidget,
                         {"maxZoom": 18,
                          "minZoom": 1,
                          "zoomDelta": 1,
                          "touchZoom": False,
                          "zoomControl": False,
                          "doubleClickZoom": False,
                          "scrollWheelZoom": True,
                          "attributionControl": False,
                          "drawCircleControl": False
                          })
        self.map.setView([39.973734, 32.761588], 18)
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)
        self.map.clicked.connect(self.map_click)

        layout = QHBoxLayout()
        info_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()
        x_coordinate_layout = QVBoxLayout()
        y_coordinate_layout = QVBoxLayout()

        right_layout.setAlignment(Qt.AlignTop)

        self.lbl_x_coordinate_vehicle = QLabel()
        self.lbl_y_coordinate_vehicle = QLabel()
        self.lbl_x_coordinate_goal = QLabel()
        self.lbl_y_coordinate_goal = QLabel()

        btn_start = QPushButton("Start")
        btn_goal = QPushButton("Goal")
        btn_step = QPushButton("Step")
        btn_obstacle = QPushButton("Obstacle")
        btn_start.clicked.connect(self.start_btn_clicked)
        btn_goal.clicked.connect(self.goal_btn_clicked)
        btn_step.clicked.connect(self.run)
        btn_obstacle.clicked.connect(self.obstacle_btn_clicked)

        layout.addLayout(info_layout)
        layout.addLayout(right_layout)
        info_layout.addWidget(self.mapWidget)
        info_layout.addLayout(bottom_layout)
        right_layout.addWidget(btn_start)
        right_layout.addWidget(btn_goal)
        right_layout.addWidget(btn_step)
        right_layout.addWidget(btn_obstacle)
        bottom_layout.addLayout(x_coordinate_layout)
        bottom_layout.addLayout(y_coordinate_layout)
        x_coordinate_layout.addWidget(self.lbl_x_coordinate_vehicle)
        x_coordinate_layout.addWidget(self.lbl_x_coordinate_goal)
        y_coordinate_layout.addWidget(self.lbl_y_coordinate_vehicle)
        y_coordinate_layout.addWidget(self.lbl_y_coordinate_goal)

        self.setLayout(layout)
        self.show()

    def colorPicker(self):
        i = self.colorNumber % 10
        result = self.colorCodes[i]
        self.colorNumber += 1
        return result

    def start_btn_clicked(self):
        self.buttonMode = "START"
        if self.startMarker is not None:
            self.map.removeLayer(self.startMarker)

    def obstacle_btn_clicked(self):
        self.buttonMode = "OBSTACLE"
        self.open_set.clear()
        self.open_set[self.calc_index(self.start_node)] = self.start_node
        self.goal_node.grid = self.calc_goal_grid()
        print("Start Node x :", self.start_node.x)
        print("Start Node y :", self.start_node.y)
        print("Start Node cost :", self.start_node.y)
        print("Start Node parent_index :", self.start_node.parent_index)
        print("Start Node grid :", self.start_node.grid)

        print("Goal Node x :", self.goal_node.x)
        print("Goal Node y :", self.goal_node.y)
        print("Goal Node cost :", self.goal_node.y)
        print("Goal Node parent_index :", self.goal_node.parent_index)
        print("Goal Node grid :", self.goal_node.grid)

        # x, y, cost, parent_index, grid

    def goal_btn_clicked(self):
        self.buttonMode = "GOAL"
        if self.goalMarker is not None:
            self.map.removeLayer(self.goalMarker)

    def map_click(self, json_point):
        # print(json_point)
        point = json_point["latlng"]["lat"], json_point["latlng"]["lng"]

        if self.buttonMode == "START":
            startPoint = [round(float(point[0]), 6), round(float(point[1]), 6)]
            self.lbl_x_coordinate_vehicle.setText("Start X : " + str(startPoint[0]))
            self.lbl_y_coordinate_vehicle.setText("Start Y : " + str(startPoint[1]))
            self.startMarker = L.circleMarker(startPoint, {"color": "#3FF00F", "radius": 5})
            self.startMarker.bindPopup('START')
            self.map.addLayer(self.startMarker)
            self.start_node = self.Node(x=startPoint[0], y=startPoint[1], cost=0.0, parent_index=-1, grid=(0, 0))
            ##@@print(startPoint)

        elif self.buttonMode == "GOAL":
            goalPoint = [round(float(point[0]), 6), round(float(point[1]), 6)]
            self.lbl_x_coordinate_goal.setText("Goal X : " + str(goalPoint[0]))
            self.lbl_y_coordinate_goal.setText("Goal Y : " + str(goalPoint[1]))
            self.goalMarker = L.circleMarker(goalPoint, {"color": '#F0370F', "radius": 5})
            self.goalMarker.bindPopup('GOAL')
            self.map.addLayer(self.goalMarker)
            self.goal_node = self.Node(x=goalPoint[0], y=goalPoint[1], cost=None, parent_index=None, grid=None)


        elif self.buttonMode == "OBSTACLE":
            obstaclePoint = [round(float(point[0]), 6), round(float(point[1]), 6)]
            self.obstacle_marker = L.circleMarker(obstaclePoint, {"color": '#F0370F', "radius": 1})
            self.obstacle_marker.bindPopup('Obstacle')
            self.map.addLayer(self.obstacle_marker)
            self.obstacleList.append(self.calc_polygon(obstaclePoint[0], obstaclePoint[1], self.obstacleRadius))

    class Node:
        def __init__(self, x, y, cost, parent_index, grid):
            self.x = x  # index of grid
            self.y = y  # index of grid
            self.cost = cost
            self.parent_index = parent_index
            self.grid = grid

    @staticmethod
    def calc_index(n1):
        return n1.grid

    @staticmethod
    def get_motion_model(step):
        # dx, dy, cost, angle
        motion = [[0, 1, step, 0],
                  [1, 1, step * 1.4, 45],
                  [1, 0, step, 90],
                  [1, -1, step * 1.4, 135],
                  [0, -1, step, 180],
                  [-1, -1, step * 1.4, 225],
                  [-1, 0, step, 270],
                  [-1, 1, step * 1.4, 315]]

        return motion

    def calc_goal_grid(self):
        xMultiplier = 1
        yMultiplier = 1
        if self.goal_node.x < self.start_node.x:
            yMultiplier = -1
        elif self.goal_node.x == self.start_node.x:
            yMultiplier = 0
        if self.goal_node.y < self.start_node.y:
            xMultiplier = -1
        elif self.goal_node.y == self.start_node.y:
            xMultiplier = 0
        startNode = (self.start_node.x, self.start_node.y)
        forYpoint = (self.goal_node.x, self.start_node.y)
        forXpoint = (self.start_node.x, self.goal_node.y)
        xDist = self.geodesic.measure(startNode, forXpoint) * 1000
        yDist = self.geodesic.measure(startNode, forYpoint) * 1000
        gridX = (int(xDist / self.stepSize)) * xMultiplier
        gridY = (int(yDist / self.stepSize)) * yMultiplier
        return gridX, gridY

    # def is_goal_closer_than_step(self):
    #     result = None
    #     min_dist_id = min(self.open_set,
    #                key=lambda o: self.geodesic.measure((self.open_set[o].x,self.open_set[o].y), (self.goal_node.x, self.goal_node.y)))
    #     if self.stepSize >= (self.geodesic.measure((self.open_set[min_dist_id].x,self.open_set[min_dist_id].y),
    #                                               (self.goal_node.x, self.goal_node.y))*1000):
    #         result = min_dist_id
    #     return result

    def calc_neighbor(self, current, i):
        newGrid = (current.grid[0] + self.motion[i][0], current.grid[1] + self.motion[i][1])
        if newGrid in self.open_set:
            return None  # Open set içinde varsa None döner
        else:
            p1 = geopy.Point(current.x, current.y)
            d = geopy.distance.geodesic(kilometers=self.motion[i][2] / 1000)
            coord = d.destination(point=p1, bearing=self.motion[i][3]).format_decimal()
            coord = coord.split(",")
            x = round(float(coord[0]), 6)
            y = round(float(coord[1]), 6)
            cost = current.cost + self.motion[i][2]
            return [x, y, cost, newGrid]

    def is_in_obstacle(self, n1):
        result = False
        p1 = Point(n1.x, n1.y)
        for node in self.obstacleList:
            result = node.contains(p1)
            if result:
                return result
        return result

    def obstacle_add(self, x, y):
        p1 = Point(x, y)
        result = False
        for obst in self.obstacleList:
            if obst.contains(p1):
                result = True
                break
        if not result:
            self.obstacleList.append(self.calc_polygon(x, y, self.obstacleRadius))

    # def is_in_openSet(self, n1, n_id):
    #     result = False
    #     if n_id in dict.keys(self.open_set):
    #         result = True
    #         return result
    #     else:
    #         p1 = Point(n1.x, n1.y)
    #         for node in self.open_set.values():
    #             poly = node.poly
    #             result = poly.contains(p1)
    #             if result:
    #                 return result
    #     return result

    @staticmethod
    def calc_polygon(x, y, stepSize):
        coords = []
        coords.clear()
        p1 = geopy.Point(x, y)
        d = geopy.distance.geodesic(kilometers=((stepSize * 0.75 * 1.4) / 1000))
        for i in range(4):
            coord = d.destination(point=p1, bearing=((90 * i) + 45)).format_decimal()
            coord = coord.split(",")
            xn = float(coord[0])
            yn = float(coord[1])
            coords.append((xn, yn))
        poly = Polygon(coords)
        return poly

    def calc_heuristic(self, n1, n2):
        a = n1.x, n1.y
        b = n2.x, n2.y
        heuristic = self.geodesic.measure(a, b) * 1000
        return heuristic

    def calc_final_path(self):
        # generate final course
        rx, ry = [self.goal_node.x], [self.goal_node.y]
        parent_index = self.goal_node.parent_index
        while parent_index != -1:
            n = self.closed_set[parent_index]
            rx.append(n.x)
            ry.append(n.y)
            parent_index = n.parent_index
        self.timePathFin = time.time()

        for i in range(len(rx) - 1):
            self.draw_line(rx[i], ry[i], rx[i + 1], ry[i + 1])
        self.timeDrawFin = time.time()
        print("Path Find Time : ", (self.timePathFin-self.timeStart))
        print("Draw Time", (self.timeDrawFin-self.timeStart))

    def draw_line(self, x1, y1, x2, y2):
        pathMarkers = L.polyline([[x1, y1], [x2, y2]], {
            "color": "red",
            "weight": 3,
            "opacity": 1,
            "lineJoin": "round",
            "smoothFactor": 1
        })
        pathMarkers.addTo(self.map)

    def planning(self):

        time1 = time.time()

        if len(self.open_set) == 0:
            print("Open set is empty..")
            return 0

        timeMin1 = time.time()
        c_id = min(self.open_set,
                   key=lambda o: self.open_set[o].cost + self.calc_heuristic(self.goal_node, self.open_set[o]))
        timeMin2 = time.time()
        print("Min bulma zamanı : ", timeMin2-timeMin1)
        ##@@print("seçilen ID : ", c_id)
        current = self.open_set[c_id]
        ##@@print("current.grid : ", current.grid)
        # #####################################################
        # self.current_marker = L.circleMarker([current.x, current.y], {"color": "#000000", "radius": 1})
        # self.current_marker.bindPopup(c_id)
        # self.map.addLayer(self.current_marker)
        # #####################################################

        if self.goal_node.grid in self.open_set:
            print("Find goal")
            self.goal_node.parent_index = self.open_set[self.goal_node.grid].parent_index
            self.goal_node.cost = current.cost
            self.calc_final_path()
            time2 = time.time()
            print("time1-time :", (time2- time1))

            a = self.start_node.x, self.start_node.y
            b = self.goal_node.x, self.goal_node.y
            print("Mesafe : ", self.geodesic.measure(a, b) * 1000)
            return 1

        del self.open_set[c_id]
        self.closed_set[c_id] = current

        color = self.colorPicker()

        for i in range(len(self.motion)):  # 8 adet komşu
            neighbor = self.calc_neighbor(current, i)
            if neighbor is None:
                continue
            node = self.Node(x=neighbor[0], y=neighbor[1], cost=neighbor[2], parent_index=c_id, grid=neighbor[3])
            n_id = self.calc_index(node)

            # If the node is not safe, do nothing
            if self.is_in_obstacle(node):
                continue

            if n_id in self.closed_set:
                continue

            if n_id not in self.open_set:
                self.open_set[n_id] = node
                # ######################################################
                # self.neighbor_marker = L.circleMarker([node.x, node.y], {"color": color, "radius": 1})
                # self.neighbor_marker.bindPopup(n_id)
                # self.map.addLayer(self.neighbor_marker)
                # ######################################################
            else:
                if self.open_set[n_id].cost > node.cost:
                    # This path is the best until now. record it
                    self.open_set[n_id] = node

    def run(self):
        self.timeStart = time.time()
        # self.planning()
        result = None
        while result == None:
            result = self.planning()



app = QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
