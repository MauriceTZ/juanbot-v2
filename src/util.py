from math import sin, copysign


def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def sin_ramp(x, pot):
    return copysign(abs(sin(x))**pot, sin(x))
