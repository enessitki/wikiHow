from classes.GnssReceiver import GnssReceiver
import time
from geopy import distance as dist
from geographiclib.geodesic import Geodesic
import math


class CoordinateConverter:
    def __init__(self, reference=None):
        self.reference = reference

    def degree_to_meter(self, location, reference=None):
        ref = self.get_reference(reference)
        assert ref is not None
        heading = self.get_heading(ref, location)
        print("heading", heading)
        heading = heading/180*math.pi

        distance = dist.distance(ref, location).meters
        return distance * math.sin(heading), distance * math.cos(heading)

    def meter_to_degree(self, location, reference=None):
        ref = self.get_reference(reference)
        assert ref is not None
        x = location[0]
        y = location[1]

        heading = (math.tan(x/y))*180/math.pi
        print("x,y heading", heading)
        distance = ((x**2)+(y**2))**(1/2)

        d = dist.geodesic(kilometers=(distance/1000))
        newCoordinate = d.destination(point=ref, bearing=heading).format_decimal()
        return newCoordinate


    def get_heading(self, location1, location2, mode="metric", reference=None):  # mode metric or degree
        a = Geodesic.WGS84.Inverse(location1[0], location1[1], location2[0], location2[1])
        heading = a["azi1"]
        return heading

    def get_reference(self, reference):
        return self.reference if reference is None else reference




class CoordinateProcessor:
    def __init__(self):
        self.receiver = GnssReceiver()
        self.receiver.connect_on_location_parsed(self.on_location_changed)

    def on_location_changed(self, location):
        print("here", location)


sp = [39.97315721162171, 32.76071012020112]
gp = [39.97386841051092, 32.76172399520875]
print("actual distance:", dist.distance(sp, gp).meters)
converter = CoordinateConverter(sp)
gp_xy = converter.degree_to_meter(gp)
dp_app = converter.meter_to_degree(gp_xy)
print("|x,y|", ((gp_xy[0]**2)+(gp_xy[1]**2))**(1/2))


