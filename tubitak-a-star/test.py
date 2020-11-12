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
        self.goalPoint = None
        self.startPoint = None
        self.obstaclePoint = None
        self.obstacleList = []
        self.obstacleRadius = 3  # Meter
        self.vehicleLastKnownLocation = [None, None]
        self.startMarker = None
        self.goalMarker = None
        self.vehicleMarker = None
        self.testVehiclepoint = ([0, 0])
        self.testVehicleMarker = None
        self.nextPointList = []
        self.openSet = []  # (point, gScore, fScore)
        self.comeFrom = []  # self.comeFrom["komşu"] = current
        self.stepSize = 1.0  # meter
        self.currentPoint = None

        self.geodesic = geodesic()



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

        self.map.setView([39.973734, 32.761588], 10)
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
        self.isStartButtonClicked = False
        self.isGoalButtonClicked = False
        self.isObstacleButtonClicked = True

    def goal_btn_clicked(self):
        self.isStartButtonClicked = False
        self.isGoalButtonClicked = True
        self.isObstacleButtonClicked = False
        if self.goalMarker is not None:
            self.map.removeLayer(self.goalMarker)

    def map_click(self, json_point):
        print(json_point)
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
            print(self.startPoint)


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
            print(self.goalPoint)

        elif self.isStartButtonClicked is False and self.isGoalButtonClicked is False and self.isObstacleButtonClicked is True:
            self.obstaclePoint = [float(point[0]), float(point[1])]
            self.obstacle_marker = L.circleMarker(self.obstaclePoint, {"color": '#F0370F', "radius": 1})
            self.obstacle_marker.bindPopup('Obstacle')
            self.map.addLayer(self.obstacle_marker)
            self.obstaclePoint.clear()
            self.obstaclePoint = (float(point[0]), float(point[1]))
            self.obstacleList.append(self.obstaclePoint)



    # def read_gps_data(self):
    #     if self.gnssSerialDevice.in_waiting > 0:
    #         sentences = self.gnssSerialDevice.read(self.gnssSerialDevice.in_waiting)
    #         p0 = sentences.find(b'$GNGGA')
    #         if p0 > -1:
    #             gga = sentences[p0:].split(b"\r\n")[0]
    #             # print(gga)
    #             try:
    #                 msg_parsed = pynmea2.parse(gga.decode())
    #                 if hasattr(msg_parsed, "latitude"):
    #                     self.vehicleLastKnownLocation = [(msg_parsed.latitude), (msg_parsed.longitude)]
    #                     if self.vehicleMarker is not None:
    #                         self.map.removeLayer(self.vehicleMarker)
    #
    #                     self.vehicleMarker = L.circle(self.vehicleLastKnownLocation, {"color": '#0F27F0', "radius": 1})
    #                     self.map.addLayer(self.vehicleMarker)
    #
    #                     # print("Arac konumu : " + str(self.vehicleLastKnownLocation))
    #             except pynmea2.ParseError as error:
    #                 print(error)

    def draw_path(self):
    #     if self.startPoint is not None and self.goalPoint is not None:
    #         if self.testVehiclepoint == ([0, 0]):
    #             self.testVehiclepoint = self.startPoint
    #         a = Geodesic.WGS84.Inverse(self.testVehiclepoint[0], self.testVehiclepoint[1], self.goalPoint[0], self.goalPoint[1])
    #         geopyVehiclePoint = geopy.Point(self.testVehiclepoint[0], self.testVehiclepoint[1])
    #         d = geopy.distance.geodesic(kilometers = 0.1)
    #         print(a["azi1"])
    #         newCoordinate = d.destination(point=geopyVehiclePoint, bearing=a["azi1"]).format_decimal()
    #         newCoordinate=newCoordinate.split(",")
    #         self.testVehiclepoint[0] = float(newCoordinate[0])
    #         self.testVehiclepoint[1] = float(newCoordinate[1])
    #         print(self.testVehiclepoint)
    #         self.testVehicleMarker = L.circle(self.testVehiclepoint, {"color": "#0FF0E6", "radius": 5})
    #         self.startMarker.bindPopup('Vehicle')
    #         self.map.addLayer(self.testVehicleMarker)
        pass

    def planner(self):
        self.openSet.clear()
        self.openSet.append((self.startPoint, 0, self.calc_fScore(self.startPoint)))
        if self.startPoint is not None and self.goalPoint is not None:
            while len(self.openSet) != 0:
                self.assign_min_fScore_point_to_currentPoint_in_openSet_and_remove_openSet()
                self.calc_next_point(self.currentPoint[0], 4)
                for neighbor in self.nextPointList:
                    if self.is_fScore_lower_than_step(neighbor):
                        break
                        self.plan_path(self.currentPoint)  # !!!!!!!!!!!!!!!!!- DONE -!!!!!!!!!!!!!!!!!

                    elif self.is_point_in_obstacle_radius(neighbor):
                        continue

                    else:
                        if not self.is_openSet_include_point(neighbor):
                            gScoreForNeighbor = self.currentPoint[1]+self.calc_gScore(neighbor, self.currentPoint[0])
                            fScoreForNeighbor = self.calc_fScore(neighbor)
                            self.openSet.append([neighbor, gScoreForNeighbor, fScoreForNeighbor])
                            self.comeFrom.append((neighbor, self.currentPoint[0]))





    def calc_fScore(self, point1):
        # cleveland_oh = (41.499498, -81.695391)
        return self.geodesic.measure(point1, self.goalPoint)*1000

    def calc_gScore(self, point1, point2):
        return self.geodesic.measure(point1, point2)*1000

    def calc_tentative_gScore(self, point1):
        tentativeGScore = self.currentPoint[1] + self.calc_gScore(self.currentPoint[0], point1)
        return tentativeGScore

    def is_openSet_include_point(self, point1):
        result = False
        for i in range(len(self.openSet)):
            if self.openSet[i][0] == point1[0]:
                result = True
        return result

    def calc_next_point(self, point1, pointNumber):
        self.nextPointList.clear()
        d = geopy.distance.geodesic(kilometers=self.stepSize / 1000)
        point = geopy.Point(point1[0], point1[1])
        angle = 360 / pointNumber
        for i in range(pointNumber):
            newCoordinate = d.destination(point=point, bearing=angle*i).format_decimal()
            newCoordinate=newCoordinate.split(",")
            a = float(newCoordinate[0])
            b = float(newCoordinate[1])
            self.nextPointList.append((a, b))

    def is_fScore_lower_than_step(self, point1):
        fScore = self.calc_fScore(point1)
        if fScore > self.stepSize:
            return False
        else:
            return True
    def is_point_in_obstacle_radius(self, point1):
        result = False
        pointNumber = 12
        coords = []
        coords.clear()
        if len(self.obstacleList) > 0:
            for i in range(len(self.obstacleList)):
                p1 = Point(point1[0], point1[1])
                d = geopy.distance.geodesic(kilometers=self.obstacleRadius / 1000)
                obstaclePoint = geopy.Point(self.obstacleList[i][0], self.obstacleList[i][1])
                angle = 360 / pointNumber
                for i in range(pointNumber):
                    newCoordinate = d.destination(point=obstaclePoint, bearing=angle*i).format_decimal()
                    newCoordinate = newCoordinate.split(",")
                    a = float(newCoordinate[0])
                    b = float(newCoordinate[1])
                    coords.append((a, b))
                poly = Polygon(coords)
                result = p1.within(poly)
                if result:
                    return result
        return result





    def plan_path(self, point):
        return 0
    def assign_min_fScore_point_to_currentPoint_in_openSet_and_remove_openSet(self):
        current = self.openSet[0]
        currentIndex = 0
        for i in range(len(self.openSet)):
            if self.openSet[i][2] < current[2]:
                currentIndex = i
        self.currentPoint = self.openSet[currentIndex]
        print(self.currentPoint)
        self.openSet.pop(currentIndex)














app = QApplication(sys.argv)
w = Window()
app.exec_()
sys.exit()
