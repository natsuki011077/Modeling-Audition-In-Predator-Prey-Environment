### Q320: Spring 2012
### Cognitive Science Program, Indiana University
### Michael Gasser: gasser@cs.indiana.edu
###
### Miscellaneous utility functions

import math, random
from functools import reduce

def reduce_lists(lists):
    '''Flatten a list of lists (doesn't mutate lists).'''
    return reduce(lambda x, y: x + y, lists)

def some(pred, seq):
    '''Returns the first successful application of pred to elements in seq.'''
    for x in seq:
        px = pred(x)
        if px:
            return px
    return False

def normalize(vector):
    '''Make the vector (really a list) length 1.0.'''
    total = math.sqrt(sum([x**2 for x in vector]))
    for i in range(len(vector)):
        vector[i] /= total

def dot_product(v1, v2):
    '''Dot product of the two vectors.'''
    return sum([x1 * x2 for x1, x2 in zip(v1, v2)])

def threshold(inp, thresh, min_val, max_val):
    '''Simple threshold function.'''
    if inp >= thresh:
        return max_val
    else:
        return min_val

def sigmoid(inp, thresh, gain):
    '''Sigmoid function (0 < y < 1) with threshold and gain.'''
    return 1.0 / (1.0 + math.exp(gain * (-inp + thresh)))

def sigmoid_slope(x):
    '''Slope of the sigmoid with output x.'''
    return x * (1.0 - x)

def get_point_dist(x1, y1, x2, y2, wrap_x=0, wrap_y=0):
    '''Integer Euclidian distance between points x1,y1 and x2,y2.

    If wrap_x and/or wrap_y are non-zero, finds the shortest distance,
    including one found by wrapping around the bottom or right side of
    the space.'''
    xdiff = x1 - x2
    if wrap_x:
        xdiff = min(abs(xdiff), abs(x1 + wrap_x - x2), abs(x2 + wrap_x - x1))
    ydiff = y1 - y2
    if wrap_y:
        ydiff = min(abs(ydiff), abs(y1 + wrap_y - y2), abs(y2 + wrap_y - y1))
    return int(math.sqrt(xdiff * xdiff + ydiff * ydiff))

def get_point_angle(x1, y1, x2, y2, wrap_x=0, wrap_y=0):
    '''Angle in integer degrees between points x1,y1 and x2,y2.

    Angles are measured counter-clockwise starting from horizontal
    left-to-right.
    
    1--2:  0

    2
    |   :  90
    1

    2--1:  180

    1
    |   :  270
    2

    If wrap_x and/or wrap_y are non-zero, finds the angle of the shortest
    line between the points, including one drawn by wrapping around the bottom
    or right side of the space.
    '''
    xdiff = x2 - x1
    if wrap_x:
        if abs(x2 + wrap_x - x1) < abs(xdiff):
            xdiff = x2 + wrap_x - x1
        elif abs(x2 - x1 - wrap_x) < abs(xdiff):
            xdiff = x2 - x1 - wrap_x
    ydiff = y1 - y2
    if wrap_y:
        if abs(y1 + wrap_y - y2) < abs(ydiff):
            ydiff = y1 + wrap_y - y2
        elif abs(y1 - y2 - wrap_y) < abs(ydiff):
            ydiff = y1 - y2 - wrap_y
    if xdiff != 0:
        tang = float(ydiff) / xdiff
    else:
        tang = 1000.0
    ang = round(math.degrees(math.atan(tang)))
    if xdiff < 0 or ydiff < 0:
        ang += 180
    if ang < 0:
        ang += 360
    return int(ang)

def xy_dist(angle, dist):
    '''The x and y distances (ints) corresponding to a distance dist in angle.'''
    radian_angle = math.radians(360 - angle)
    return int(dist * math.cos(radian_angle)), int(dist * math.sin(radian_angle))

def get_endpoint(x1, y1, angle, dist):
    '''Coordinates of end of line that starts at x1,y1 at given angle and dist.'''
    return x1 + int(round(dist * math.cos(math.radians(360 - angle)))), \
           y1 + int(round(dist * math.sin(math.radians(360 - angle))))

def exp_luce_choice(seq, mult = 1.0):
    '''Choose index of value in seq, treating value as probabilistic weight.'''
    exp_seq = [math.exp(x * mult) for x in seq]
    total = sum(exp_seq)
    if total:
        ran = random.random()
        scaled_total = 0.0
        for index, elem in enumerate(exp_seq):
            scaled_total += elem / total
            if ran < scaled_total:
                return index
        # In case we haven't found it (because of rounding errors?), return the last index
        return len(seq) - 1
    else:
        # All values are 0; pick a random position
        return random.randint(0, len(seq) - 1)

def bin_to_dec(bin):
    '''Convert a list of booleans to the corresponding decimal number.'''
    sum = 0
    for power, b in enumerate(reversed(bin)):
        if b:
            sum += pow(2, power)
    return sum

