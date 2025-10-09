def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def ramp(x, in_min, in_max, out_min, out_max, vel):
    return map_range(x, in_min, in_max, out_min, out_max)