import math
import numpy as np
import sys
import time
# import pynmea2
# import serial
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
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

        self.isStartButtonClicked = False
        self.isGoalButtonClicked = False
        self.isObstacleButtonClicked = False

        self.startMarker = None
        self.goalMarker = None

        self.goalPoint = None
        self.startPoint = None
        self.obstaclePoint = None
        self.obstacleList = []
        self.obstacleRadius = 3  # Meter
        self.neighborCount = 4
        self.nextPointList = []
        self.openSet = []  # (point, gScore, fScore)
        self.comeFrom = []  # self.comeFrom["komşu"] = current
        self.stepSize = 10.0  # meter
        self.currentPoint = None
        self.indexForRemoveFromOpenSet = None
        self.cicle = 0

        self.geodesic = geodesic()

        self.current_marker = None

        # self.gnssSerialDevice = serial.Serial(
        #     port='COM7',
        #     baudrate=115200,
        #     parity=serial.PARITY_NONE,
        #     stopbits=serial.STOPBITS_ONE,
        #     bytesize=serial.EIGHTBITS,
        #     timeout=0)

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
        btn_step.clicked.connect(self.planner)
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

    def start_btn_clicked(self):
        self.isStartButtonClicked = True
        self.isGoalButtonClicked = False
        self.isObstacleButtonClicked = False
        if self.startMarker is not None:
            self.map.removeLayer(self.startMarker)

    def obstacle_btn_clicked(self):
        # self.isStartButtonClicked = False
        # self.isGoalButtonClicked = False
        # self.isObstacleButtonClicked = True
        self.openSet.clear()
        self.openSet.append((self.startPoint, 0, self.calc_fScore(self.startPoint, 0)))

    def goal_btn_clicked(self):
        self.isStartButtonClicked = False
        self.isGoalButtonClicked = True
        self.isObstacleButtonClicked = False
        if self.goalMarker is not None:
            self.map.removeLayer(self.goalMarker)

    def map_click(self, json_point):
        # print(json_point)
        point = json_point["latlng"]["lat"], json_point["latlng"]["lng"]

        if self.isStartButtonClicked is True and self.isGoalButtonClicked is False and self.isObstacleButtonClicked is False:
            self.startPoint = [float(point[0]), float(point[1])]
            self.isStartButtonClicked = False
            self.isGoalButtonClicked = False
            self.lbl_x_coordinate_vehicle.setText("Start X : " + str(self.startPoint[0]))
            self.lbl_y_coordinate_vehicle.setText("Start Y : " + str(self.startPoint[1]))
            self.startMarker = L.circleMarker(self.startPoint, {"color": "#3FF00F", "radius": 5})
            self.startMarker.bindPopup('START')
            self.map.addLayer(self.startMarker)
            self.startPoint.clear()
            self.startPoint = (float(point[0]), float(point[1]))
            # print(self.startPoint)


        elif self.isStartButtonClicked is False and self.isGoalButtonClicked is True and self.isObstacleButtonClicked is False:
            self.goalPoint = [float(point[0]), float(point[1])]
            self.isStartButtonClicked = False
            self.isGoalButtonClicked = False
            self.lbl_x_coordinate_goal.setText("Goal X : " + str(self.goalPoint[0]))
            self.lbl_y_coordinate_goal.setText("Goal Y : " + str(self.goalPoint[1]))
            self.goalMarker = L.circleMarker(self.goalPoint, {"color": '#F0370F', "radius": 5})
            self.goalMarker.bindPopup('GOAL')
            self.map.addLayer(self.goalMarker)
            self.goalPoint.clear()
            self.goalPoint = (float(point[0]), float(point[1]))
            # print(self.goalPoint)

        elif self.isStartButtonClicked is False and self.isGoalButtonClicked is False and self.isObstacleButtonClicked is True:
            self.obstaclePoint = [float(point[0]), float(point[1])]
            self.obstacle_marker = L.circleMarker(self.obstaclePoint, {"color": '#F0370F', "radius": 1})
            self.obstacle_marker.bindPopup('Obstacle')
            self.map.addLayer(self.obstacle_marker)
            self.obstaclePoint.clear()
            self.obstaclePoint = (float(point[0]), float(point[1]))
            self.obstacleList.append(self.obstaclePoint)

    def planner(self):

        pass

    def find_min_fScore(self):
        