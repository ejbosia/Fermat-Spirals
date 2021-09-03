'''
Labyrinth
Contains functions for creating organic labyrinths and mazes, as presented in "Organic Labyrinths and Mazes": http://www.dgp.toronto.edu/~karan/pdf/mazes.pdf

@author ejbosia
'''

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("distance", help="distance between lines", type = float)
parser.add_argument("-a","--pushpull", help="push-pull multiplier", type = float)
parser.add_argument("-b", "--brownian", help="brownian mulitplier", type = float)
parser.add_argument("-f", "--fairing", help="enable output", type= float)
parser.add_argument("-m", "--metrics", help="enable metrics", action='store_true')



from shapely.geometry import Point, LinearRing, LineString

from math import sqrt, cos, sin, pi, atan2
from random import normalvariate, random

from dataclasses import dataclass

from matplotlib import pyplot
from matplotlib.animation import FuncAnimation, PillowWriter

from logging import Logger, INFO, DEBUG

from shapely_utilities import sample

from shapely_conversion import convert

from numba import jit, void, double

from numba import types
from numba.typed import Dict

import numpy as np
import cv2
import os

logger = Logger(__name__)
logger.setLevel(DEBUG)


@jit(nopython=True)
def closest(A,B,C):

    e1 = np.array([B[0] - A[0], B[1] - A[1]])
    e2 = np.array([C[0] - A[0], C[1] - A[1]])

    dp = np.dot(e1, e2)

    if dp < 0:
        return A
    if dp > np.dot(e1,e1):
        return B

    len2 = e1[0] * e1[0] + e1[1] * e1[1]

    return np.array(((A[0] + (dp * e1[0]) / len2),(A[1] + (dp * e1[1]) / len2)))


@jit(nopython=True)
def neighbor_indices(i1, length):
    i0 = i1 - 1 if i1 > 0 else length-1
    i2 = i1 + 1 if i1+1 < length else 0
    
    return [i0, i1, i2]

'''
Calculate the smoothing force on a point (at index i1)
'''
@jit(nopython=True)
def smoothing_force(i0,i1,i2,points):

    p0 = points[i0]
    p1 = points[i1]
    p2 = points[i2]

    d0 = np.sqrt((p1[0]-p0[0])**2 + (p1[1]-p0[1])**2)
    d2 = np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    dx = (p0[0]*d2+p2[0]*d0)/(d0+d2) - p1[0]
    dy = (p0[1]*d2+p2[1]*d0)/(d0+d2) - p1[1]

    return (dx, dy)


'''
Calculate the push pull force on a point
    - only include points within a distance
    - use lennard jones potential to get the force
'''
@jit(nopython=True)
def pushpull_force(i0,i1,i2, points, config, d):

    # get the point
    p1 = points[i1]

    avoid = {i0,i1,i2}

    dx = 0
    dy = 0
    counter = 0

    # determine the valid points by comparing each linestring
    for i in range(len(points)-1):
        
        if i in avoid or i+1 in avoid or -1 in avoid:
            continue
        
        p2 = closest(points[i], points[i+1], p1)
        
        if abs(p1[0]-p2[0]) > config["R1"] or abs(p1[1]-p2[1]) > config["R1"]:
            continue
        
        d2 = (p1[0]-p2[0])**2+(p1[1]-p2[1])**2

        if d2 < config["R12"]:

            dis = np.sqrt(d2)

            r = dis/(config["D"] * d)

            E = (config["R0"]/r)**12-(config["R0"]/r)**6 
                                    
            dx += E * (p1[0]-p2[0])/dis
            dy += E * (p1[1]-p2[1])/dis
            counter += 1

    if counter == 0:
        return (0,0,0)

    dx /= counter
    dy /= counter

    # clamp the force to D
    d = sqrt(dx**2+dy**2)
    if d > config["CLAMP"]:
        dx = dx/d * config["CLAMP"]
        dy = dy/d * config["CLAMP"]

    return (dx, dy, counter)


'''
Run an update step on the points
'''
@jit(nopython=True)
def update(points, config, d):

    bx = 0
    by = 0
    fx = 0
    fy = 0
    ax = 0
    ay = 0
    
    length = len(points)

    # calculate the force vectors for every point and update the point
    for i in range(len(points)):

        i0,i1,i2 = neighbor_indices(i, length)

        if config["F"] > 0:
            f = smoothing_force(i0,i1,i2, points)
        if config["A"] > 0:
            a = pushpull_force(i0,i1,i2, points, config, d)
            
            
        x = config["A"]*a[0] + config["F"]*f[0]
        y = config["A"]*a[1] + config["F"]*f[1]

        points[i][0] +=  x
        points[i][1] +=  y


def optimize(path, D, iterations=1):

    points = sample(path, D)

    points = np.array([(p[0],p[1],1) for p in points.coords])

    config = Dict.empty(
        key_type=types.unicode_type,
        value_type = types.float64
    )

    config["A"] = 0.008
    config["B"] = 0.05
    config["F"] = 0.1
    config["k0"] = 1.0
    config["k1"] = 5.0
    config["kmin"] = 0.2
    config["kmax"] = 0.5
    config["D"] = float(D)
    config["FROZEN"] = 250

    config["R0"] = config["k0"] * config["D"]
    config["R1"] = config["k1"] * config["D"]
    config["R12"] = config["R1"]**2

    config["CLAMP"] = 20.0*D

    for _ in range(iterations):
        points = update(points, config, 1)

    return points
