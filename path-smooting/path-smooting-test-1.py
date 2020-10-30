import math
import matplotlib.pyplot as plt
import numpy as np


def solve(x0, y0, x1, y1, th):
    eqs = np.array([[x1**2, x1, 1],
                  [2*x0 , 1 , 0],
                  [2 , 0 , 0]])
                  # [2*x0 , 1 , 0]])
    ans = np.array([y1, math.tan(math.pi/36), 1/(math.cos(th)**2)])
    # ans = np.array([y0, y1, math.tan(math.pi/36)])
    return tuple(np.linalg.solve(eqs, ans))


LIMIT = 10
waypoints_x = np.array([1, 5])
waypoints_y = np.array([0, 3])
for theta in range(360):
    theta_0 = theta * math.pi / 180
    a, b, c = solve(waypoints_x[0], waypoints_y[0], waypoints_x[1], waypoints_y[1], theta_0)
    x = np.linspace(waypoints_x[0], waypoints_x[1], 100)
    y = a*(x**2) + b*x + c
    print(a, b, c)
    plt.clf()
    plt.plot(waypoints_x, waypoints_y, "o")
    plt.plot(x, y, ".-r")
    plt.xlim(-LIMIT, LIMIT)
    plt.ylim(-LIMIT, LIMIT)
    plt.pause(0.1)
