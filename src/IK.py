import numpy as np
# Solver para pierna con 2 motores o links


class Pierna:
    def __init__(self, l1: float, l2: float, s1, s2, s3, s4, d1=True, d2=True, d3=True, d4=True,
                 o1=0, o2=0, o3=0, o4=0, xoff=0, yoff=0):
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

        self.o1 = o1
        self.o2 = o2
        self.o3 = o3
        self.o4 = o4
        self.xoff = xoff
        self.yoff = yoff

        self.x = None
        self.y = None

    def angulos(self, x, y, a=0, p=0):
        self.x = x
        self.y = y
        x, y = y+self.yoff, x+self.xoff
        y = -y
        q2 = np.acos((x*x + y*y - self.l1 ** 2 - self.l2 ** 2) /
                     (2 * self.l1 * self.l2))

        q1 = np.atan2(y, x) - np.atan((self.l2 * np.sin(q2)) /
                                      (self.l1 + self.l2 * np.cos(q2)))
        
        self.s1.angle = ((-1)**(not self.d1) * np.rad2deg(q1) + 90 + self.o1)
        
        self.s2.angle = ((-1)**(not self.d2) * np.rad2deg(q2) + 90 + self.o2)

        self.s3.angle = ((-1)**(not self.d3) * np.rad2deg(q1 + q2) + 90 + a + self.o3)

        if self.s4.angle is None:
            self.s4.angle = 90
        self.s4.angle += ((90 + (-1)**(not self.d4) * p + self.o4) - self.s4.angle) * 0.3

        return q1, q2

    def __str__(self):
        return f"Pierna({self.s1.angle:.2f}, {self.s2.angle:.2f}, {self.s3.angle:.2f}, {self.s4.angle:.2f}, {self.x}, {self.y})"
# p = Pierna(5, 5)
# t = 0
# print(np.rad2deg(p.angulos(0, 10)))
