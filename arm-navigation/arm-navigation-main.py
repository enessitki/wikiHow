import matplotlib.pyplot as plt
import math
import typing
from trianglesolver import solve


class Link:
    def __init__(self, length, angle=0, xs=0, ys=0):
        self.angle = angle
        self.xs = xs
        self.ys = ys
        self.length = length
        self.index = 0

    def __len__(self):
        return self.length

    def is_in_reach(self, x, y):
        return ((self.xs - x) ** 2 + (self.ys - y) ** 2) <= self.length ** 2

    def get_final_point(self):
        return self.xs + self.length * math.cos(self.angle), self.ys + self.length * math.sin(self.angle)

    def update_angle_with_final_point(self, xf, yf):
        self.angle = math.atan2((yf - self.ys), (xf - self.xs))
        xf, yf = self.get_final_point()

        return xf, yf, self.angle

    def update_angle(self, angle):
        self.angle = angle

    def update_start_position(self, x0, y0):
        self.xs = x0
        self.ys = y0

    def get_angle(self):
        return self.angle

    def get_start_point(self):
        return self.xs, self.ys

    def get_plottable_points(self):
        XS = self.get_start_point()
        XF = self.get_final_point()

        return [XS[0], XF[0]], [XS[1], XF[1]]


class Arm:
    def __init__(self, lengths, initial_angles, xs=0, ys=0):
        self.nofLinks = len(lengths)
        self.lengths = lengths
        self.totalLength = sum(lengths)
        self.links = []
        for n in range(self.nofLinks):
            if n == 0:
                lxs = xs
                lys = ys
            else:
                lxs, lys = self.links[n-1].get_final_point()

            l = Link(length=lengths[n], angle=initial_angles[n], xs=lxs, ys=lys)
            l.index = n
            self.links.append(l)

    def plan_navigation_to(self, xt, yt):
        # check if target in reach
        xs, ys = self.links[0].get_start_point()
        if not self.is_in_reach(xs, ys, xt, yt, self.totalLength):
            return False

        

        # # calculate minimum nof link to reach target
        # length = 0
        # link_index = -1
        # for link in reversed(self.links):
        #     xs, ys = link.get_start_point()
        #     length += link.length
        #     print(xs, ys, xt, yt, length)
        #     if self.is_in_reach(xs, ys, xt, yt, length):
        #         link_index = link.index
        #         break
        # print(length, link_index)
        # if link_index == 0:
        #     for link in self.links:
        #         if link.index == 0:
        #             link.update_angle_with_final_point(xt, yt)
        #         else:
        #             xs, ys = self.links[link.index - 1].get_final_point()
        #             link.update_start_position(xs, ys)
        #             link.update_angle_with_final_point(xt, yt)
        #
        #     return True
        #
        # else:
        #     print(" partial move ")
        #     base_link = self.links[link_index - 1]
        #     x0, y0 = base_link.get_start_point()
        #     xi, yi = self.get_intersection(x0, y0, base_link.length, xt, yt, length)
        #     if xi is None:
        #         return False
        #     elif type(xi) == list:
        #         # select one of the two solution
        #         xi = xi[0]
        #         yi = yi[0]
        #
        #     base_link.update_angle_with_final_point(xi, yi)
        #     for link in self.links[link_index:]:
        #         # if link.index == link_index:
        #         #     link.update_start_position()
        #         #     link.update_angle_with_final_point(xt, yt)
        #         # else:
        #         xs, ys = self.links[link.index - 1].get_final_point()
        #         link.update_start_position(xs, ys)
        #         link.update_angle_with_final_point(xt, yt)
        #         return True

    @staticmethod
    def get_intersection(x0, y0, l0, x1, y1, l1):
        d = math.sqrt((((x0 - x1) ** 2) + ((y0 - y1) ** 2)))
        print(d, l0, l1)
        if d > l0 + l1:
            return None, None
        elif d == l0 + l1:
            angle = math.atan2(y0 - y1, x0 - x1)
            xi = x0 + l0 * math.cos(angle)
            yi = y0 + l0 * math.sin(angle)
            return xi, yi
        else: # d < l0 + l1
            print("here**", l1, l0, d)
            a, b, c, delta_angle, B, C = solve(a=l1, b=l0, c=d)
            angle = math.atan2(y0 - y1, x0 - x1)

            angle0 = angle - delta_angle
            angle1 = angle + delta_angle

            xi0 = x0 + l0 * math.cos(angle0)
            yi0 = y0 + l0 * math.sin(angle0)

            xi1 = x0 + l0 * math.cos(angle1)
            yi1 = y0 + l0 * math.sin(angle1)

            return [xi0, xi1], [yi0, yi1]



    @staticmethod
    def is_in_reach(xs, ys, xt, yt, length):
        return ((xs - xt) ** 2 + (ys - yt) ** 2) <= length ** 2

    def get_plottable_points(self):
        X, Y = self.links[0].get_plottable_points()
        for link in self.links:
            xf, yf = link.get_final_point()
            X.append(xf)
            Y.append(yf)

        return X, Y


lengths = [1, 1, 1]
initial_angles = [0, 0, 0]
LIMIT = sum(lengths)
arm = Arm(lengths=lengths, initial_angles=initial_angles, xs=0, ys=0)
arm.plan_navigation_to(0, 2)
X, Y = arm.get_plottable_points()

plt.plot(X, Y, "-ro")
plt.xlim(-LIMIT, LIMIT)
plt.ylim(-LIMIT, LIMIT)
plt.show()
# l0 = Link(length=1)
# N = 73
#
# plt.autoscale = False
# for n in range(N):
#     angle = math.pi/(N/2)*n
#     x = math.cos(angle)
#     y = math.sin(angle)
#
#     l0.update_angle_with_final_point(x, y)
#     X, Y = l0.get_plottable_points()
#     plt.plot(X, Y, "-ro")
#     plt.xlim(-1, 1)
#     plt.ylim(-1, 1)
#     plt.pause(0.2)
#     plt.clf()

# x = [1,2,3]
# y = [1,2,3]
# plt.plot(x,y, "-ro")
# plt.show()