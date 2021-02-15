import sys
import time
import threading
import math
import numpy as np
import pynmea2
import serial
import geopy
from geopy.distance import geodesic
from geographiclib.geodesic import Geodesic
from shapely.geometry import Point, Polygon

from classes.SickS300 import SickS300
from classes.GNSS import GNSS
from classes.BNO055 import IMU


class ObstacleAvoidance:
    def __init__(self):
        self.threadMoveVehicle = threading.Thread(target=self.move_vehicle)
        self.threadCalcNewPoint = threading.Thread(target=self.calc_new_point)
        self.vehicleRadius = 1  # meter
        self.maximumDistance = 10  # meter
        self.vehicleLastKnowLocation = self.Node(0, 0)
        if (self.vehicleRadius * 3) > self.maximumDistance:
            self.maximumDistance = self.vehicleRadius * 3
        self.lidar = SickS300(max_distance=self.maximumDistance)
        self.gnss = GNSS()
        self.imu = IMU()
        self.visionFieldList = self.calc_vision_field()
        self.neighborList = []
        self.secondOfCalcNewPointList = 1


    class Node:
        def __init__(self, x, y, poly=None):
            self.x = x  # index of grid
            self.y = y  # index of grid
            self.poly = poly

    # Aracın geçebileceği alanların açısını hesapalar
    def calc_vision_field(self):
        visionFieldList = []
        value = self.vehicleRadius / (self.maximumDistance - self.vehicleRadius)
        radian = math.asin(value)
        degree = float(math.degrees(radian), 2)
        realDegree = degree * 2
        visionAngle = math.ceil(realDegree)
        while 180 % visionAngle != 0:
            visionAngle += 1

        for i in range(int(180 / visionAngle)):
            startAngle = i * visionAngle
            endAngle = (i + 1) * visionAngle
            visionFieldList.append([startAngle, endAngle])
        return visionFieldList

    @staticmethod
    def calc_polygon(x, y, radius, pointCount):
        angle = 360 / pointCount
        coords = []
        coords.clear()
        p1 = geopy.Point(x, y)
        d = geopy.distance.geodesic(kilometers=((radius) / 1000))
        for i in range(pointCount):
            coord = d.destination(point=p1, bearing=(i * angle)).format_decimal()
            coord = coord.split(",")
            xn = float(coord[0])
            yn = float(coord[1])
            coords.append((xn, yn))
        poly = Polygon(coords)
        return poly

    def calc_next_coordinate(self, current, realHeading, LidarHeading):
        # Kendisine gelen anlık konum bilgisini alıp araç
        # heading'i ve lidar dan gelen uygun olan noktanın heading verisini alıp
        # yeni coordinate hesapalr ve listeye atar

        p1 = geopy.Point(current.x, current.y)
        d = geopy.distance.geodesic(kilometers=self.maximumDistance / 1000)
        newBearing = realHeading + 90 - LidarHeading
        coord = d.destination(point=p1, bearing=newBearing).format_decimal()
        coord = coord.split(",")
        x = round(float(coord[0]), 6)
        y = round(float(coord[1]), 6)
        n1 = self.Node(x, y)
        self.neighborList.append(n1)

    def read_lidar(self):
        return self.lidar.update()

    def get_heading(self):
        result = self.imu.get_euler()
        return result[0]

    def get_location(self):
        return self.gnss.read_gps_data()

    def calc_neighbors_point_list(self, lidarValue, location, realHeading):
        self.neighborList.clear()
        bannedZone = []
        for visionField in self.visionFieldList:
            for lidarAngle in lidarValue:
                if visionField[0] <= lidarAngle < visionField[1]:
                    bannedZone.append(lidarAngle)
                    break
        self.neighborList.clear()

        for i in range(len(self.visionFieldList)):
            try:
                bannedZone.index(i)
                continue
            except:
                LidarHeading = (self.visionFieldList[i][0] + self.visionFieldList[i][1]) / 2
                self.vehicleLastKnowLocation.x = location[0]
                self.vehicleLastKnowLocation.y = location[1]
                self.calc_next_coordinate(self.vehicleLastKnowLocation, realHeading, LidarHeading)

    def calc_new_point(self):
        timeCalcNewPoint = None
        bannedZone = []
        while True:
            realHeading = self.get_heading()
            location = self.get_location()
            bannedZone.clear()
            lidarValue = self.read_lidar()
            if len(lidarValue) > 0:
                self.calc_neighbors_point_list(lidarValue, location, realHeading)
                timeCalcNewPoint = time.time()
            elif (time.time() - timeCalcNewPoint) > self.secondOfCalcNewPointList:
                self.calc_neighbors_point_list(lidarValue, location, realHeading)
                timeCalcNewPoint = time.time()

    def turn_to_goal_at_start(self):
        pass

    def move_vehicle(self):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
           print("process")
        print("finish")



    def main(self):
        self.turn_goal_for_start()
        self.threadMoveVehicle.start()
        self.threadCalcNewPoint.start()



