import numpy as np
# Solver para pierna con 2 motores o links


class Pierna:
    def __init__(self, l1: float, l2: float, s1, s2, s3, s4, d1=True, d2=True, d3=True, d4=True):
        assert l1 > 0
        assert l2 > 0
        self.l1 = l1
        self.l2 = l2
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.s4 = s4
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.d4 = d4

    def angulos(self, x, y, a=0, p=0):
        x, y = y, x
        y = -y
        q2 = np.acos((x*x + y*y - self.l1 ** 2 - self.l2 ** 2) /
                     (2 * self.l1 * self.l2))

        q1 = np.atan2(y, x) - np.atan((self.l2 * np.sin(q2)) /
                                      (self.l1 + self.l2 * np.cos(q2)))
        if self.d1:
            self.s1.angle = np.rad2deg(q1) + 90
        else:
            self.s1.angle = -np.rad2deg(q1) + 90
        if self.d2:
            self.s2.angle = np.rad2deg(q2) + 90
        else:
            self.s2.angle = -np.rad2deg(q2) + 90
        if self.d3:
            self.s3.angle = np.rad2deg(q1 + q2) + 90 + a
        else:
            self.s3.angle = -np.rad2deg(q1 + q2) + 90 - a
        if self.d4:
            self.s4.angle = 90 + p
        else:
            self.s4.angle = 90 -p
        return q1, q2

# p = Pierna(5, 5)
# t = 0
# print(np.rad2deg(p.angulos(0, 10)))
