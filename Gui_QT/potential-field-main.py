import numpy
import cv2
from sympy import Function, Symbol, symbols, Piecewise
from sympy.plotting import plot

class Field:
    def __init__(self, goal_point_x, goal_point_y):
        x = symbols('x')
        y = symbols('y')
        kp = 5
        nita = 5

        self.goalFunction = (kp/2)*((x-goal_point_x)**2)+((y-goal_point_y)**2)
        self.obstacleFunction = Piecewise(
            (0.5*nita),
            ()

        )









        # ans = self.goalFunction.evalf(subs={x: 5, y: 5})
        # p1 = plot(y, show=True)





Field(2, 2)


