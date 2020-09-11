import geopy
import geopy.distance

distances = []
b = 0
for dx in range(91):

    a = geopy.distance.distance().measure((dx, 30), (dx, 31))
    print(dx, a -b)
    b = a
    distances.append(a)

print(distances)