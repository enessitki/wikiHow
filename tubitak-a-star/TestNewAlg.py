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
        self.vehicleRadius = 10  # meter
        self.maximumDistance = 1  # meter
        if (self.vehicleRadius*3) > self.maximumDistance:
            self.maximumDistance = self.vehicleRadius*3


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
        self.obstacle_marker = None

        self.startNode = None
        self.goalNode = None
        self.obstaclePolyList = []
        self.visionFieldList = []
        self.isStart = False
        self.visionAngle = None
        self.neighborList = []
        self.current = None
        self.heading = None

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

    class Node:
        def __init__(self, x, y, poly=None):
            self.x = x  # index of grid
            self.y = y  # index of grid
            self.poly = poly

    def start_btn_clicked(self):
        self.buttonMode = "START"
        if self.startMarker is not None:
            self.map.removeLayer(self.startMarker)

    def obstacle_btn_clicked(self):
        self.buttonMode = "OBSTACLE"
        heading = Geodesic.WGS84.Inverse(self.startNode.x, self.startNode.y, self.goalNode.x, self.goalNode.y)["azi2"]
        print(heading)

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
            self.startNode = self.Node(startPoint[0], startPoint[1])

        elif self.buttonMode == "GOAL":
            goalPoint = [round(float(point[0]), 6), round(float(point[1]), 6)]
            self.lbl_x_coordinate_goal.setText("Goal X : " + str(goalPoint[0]))
            self.lbl_y_coordinate_goal.setText("Goal Y : " + str(goalPoint[1]))
            self.goalMarker = L.circleMarker(goalPoint, {"color": '#F0370F', "radius": 5})
            self.goalMarker.bindPopup('GOAL')
            self.map.addLayer(self.goalMarker)
            self.goalNode = self.Node(goalPoint[0], goalPoint[1])

        elif self.buttonMode == "OBSTACLE":
            obstaclePoint = [round(float(point[0]), 6), round(float(point[1]), 6)]
            self.obstacle_marker = L.circleMarker(obstaclePoint, {"color": '#F0370F', "radius": 1})
            self.obstacle_marker.bindPopup('Obstacle')
            self.map.addLayer(self.obstacle_marker)
            self.obstaclePolyList.append(self.calc_polygon(obstaclePoint[0], obstaclePoint[1], self.maximumDistance*0.75))

    # Anlık koordinat ve heading verisi alır --> Yeni koordinatların olduğu liste çıkışı verir
    def calc_neighbor(self, current, heading):
        self.neighborList.clear()
        p1 = geopy.Point(current.x, current.y)
        d = geopy.distance.geodesic(kilometers=self.maximumDistance / 1000)
        for i in range(len(self.visionFieldList)):
            print("i : ", i)
            print("heading : ", heading)
            bearing = (heading+90-((self.visionFieldList[i][0]+self.visionFieldList[i][1])/2))
            print("bearing : ", bearing)
            coord = d.destination(point=p1, bearing=bearing).format_decimal()
            coord = coord.split(",")
            x = round(float(coord[0]), 6)
            y = round(float(coord[1]), 6)
            n1 = self.Node(x, y)
            if not self.is_in_obstacle(n1):
                self.neighborList.append(n1)


    def is_in_obstacle(self, n1):
        result = False
        p1 = Point(n1.x, n1.y)
        for node in self.obstaclePolyList:
            result = node.contains(p1)
            if result:
                return result
        return result

    def obstacle_add(self, x, y):
        p1 = Point(x, y)
        result = False
        for obst in self.obstaclePolyList:
            if obst.contains(p1):
                result = True
                break
        if not result:
            self.obstaclePolyList.append(self.calc_polygon(x, y, self.obstacleRadius))

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

    # Aracın gecenileceği alanın açılarını hesapalr
    def calc_vision_field(self):
        value = self.vehicleRadius / (self.maximumDistance-self.vehicleRadius)
        radian = math.asin(value)
        degree = float(math.degrees(radian), 2)
        realDegree = degree*2
        visionAngle = math.ceil(realDegree)
        while 180 % visionAngle != 0:
            visionAngle += 1
        self.visionFieldList.clear()
        self.visionAngle = visionAngle
        for i in range(int(180/visionAngle)):
            startAngle = i*visionAngle
            endAngle = (i+1)*visionAngle
            self.visionFieldList.append([startAngle, endAngle])

    def calc_shortest_neighbor(self):
        shortestNode = self.neighborList[0]
        dist = self.calc_heuristic(self.goalNode, shortestNode)
        for i in range(len(self.neighborList)):
            newDist = self.calc_heuristic(self.goalNode, self.neighborList[i])
            if newDist < dist:
                dist = newDist
                shortestNode = self.neighborList[i]
        return shortestNode


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
        if self.isStart is False:
            self.calc_vision_field()
            self.isStart = True
            self.current = self.startNode
            self.heading = Geodesic.WGS84.Inverse(self.startNode.x, self.startNode.y, self.goalNode.x, self.goalNode.y)["azi2"]
            print(self.heading)
        else:
            self.obstacle_marker = L.circleMarker([self.current.x, self.current.y], {"color": '#1456fa', "radius": 1})
            self.obstacle_marker.bindPopup('neighbor')
            self.map.addLayer(self.obstacle_marker)
            self.calc_neighbor(current=self.current, heading=self.heading)
            nextPoint = self.calc_shortest_neighbor()
            self.heading = Geodesic.WGS84.Inverse(self.current.x, self.current.y, nextPoint.x, nextPoint.y)["azi2"]
            print(self.heading)
            self.current = nextPoint

    def run(self):
        self.planning()
        # result = None
        # while result == None:
        #     result = self.planning()



app = QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
