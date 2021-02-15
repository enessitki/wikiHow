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
from classes.GNSS import GNSS
from classes.BNO055 import IMU

class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)
        self.setWindowTitle("Title")
        # self.timer = QTimer()
        # self.timer.setInterval(1000)
        # self.timer.timeout.connect(self.read_gps_data)
        # self.timer.start()

        self.imu = IMU()
        self.gnss = GNSS()
        self.vehicleLocation = self.Node(None, None)

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

        self.stepSize = 1
        self.obstacleRadius = 10

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



    def start_btn_clicked(self):
        self.buttonMode = "START"
        if self.startMarker is not None:
            self.map.removeLayer(self.startMarker)


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
            self.start_node = self.Node(latitude=startPoint[0], longitude=startPoint[1])
            ##@@print(startPoint)

        elif self.buttonMode == "GOAL":
            goalPoint = [round(float(point[0]), 6), round(float(point[1]), 6)]
            self.lbl_x_coordinate_goal.setText("Goal X : " + str(goalPoint[0]))
            self.lbl_y_coordinate_goal.setText("Goal Y : " + str(goalPoint[1]))
            self.goalMarker = L.circleMarker(goalPoint, {"color": '#F0370F', "radius": 5})
            self.goalMarker.bindPopup('GOAL')
            self.map.addLayer(self.goalMarker)
            self.goal_node = self.Node(latitude=goalPoint[0], longitude=goalPoint[1])

    class Node:
        def __init__(self, latitude, longitude):
            self.latitude = latitude  # index of grid
            self.longitude = longitude  # index of grid

    def get_location(self):
        return self.gnss.read_gps_data()

    def get_imu(self):
        a = self.imu.get_euler()
        return a[0]

    def run(self):
        while True:
            location = self.get_location()
            self.vehicleLocation.latitude = location[0]
            self.vehicleLocation.longitude = location[1]
            heading = Geodesic.WGS84.Inverse(self.vehicleLocation.latitude, self.vehicleLocation.longitude, self.goal_node.latitude, self.goal_node.longitude)
