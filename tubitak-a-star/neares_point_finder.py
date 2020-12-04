import time
import math
from geopy.distance import geodesic
from geopy import Point


# ref_lat_lon = [39.973751875228885, 32.76164424205761]
ref_lat_lon = [0, 90]
ref = Point(ref_lat_lon)

control_distance = 0.1
control_angle = -90
coord = geodesic().destination(point=ref, bearing=control_angle, distance=control_distance).format_decimal()

app_ref = geodesic().destination(point=coord, bearing=180 + control_angle, distance=control_distance).format_decimal()
app_ref_lat_lon = [float(x) for x in app_ref.replace(" ", "").split(",")]

print([x-y for x, y in zip(app_ref_lat_lon, ref_lat_lon)])

distance = geodesic().measure(ref, app_ref)
print(distance*1000)