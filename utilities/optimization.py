#impementation for curve optimization from paper "Connected Fermat Spirals"
import numpy as np

# if you are having problem with numpy version (https://github.com/cvxgrp/cvxpy/issues/1229) 
# I would suggest you to manually install cvxpy via their source code as this is essentially a pip problem
import cvxpy as cp

from shapely.geometry import Point
from shapely.geometry import Polygon

from shapely_utilities import sample

from functools import lru_cache

def get_coord_list(polygon):
    '''
    get all coords from polygon's exterior
    '''
    if type(polygon) is Polygon:
        return list(polygon.exterior.coords)
    elif type(polygon) is list:
        return polygon

def get_xy(polygon, local):
    '''
    convert polygon or plain path object to vectors in x, y directions
    '''
    x = []
    y = []
    
    if local:
        coord_list = get_coord_list(polygon)
        x = np.matrix([[coord[0]] for coord in coord_list])
        y = np.matrix([[coord[1]] for coord in coord_list])
    else:
        x = np.matrix([[coord[0]] for coord in polygon])
        y = np.matrix([[coord[1]] for coord in polygon])
    
    #n = np.concatenate((x, y), axis=1)
    #return n
    return (x, y)

@lru_cache(maxsize=None)
def dist(p1, p2):
    '''
    calculate the distance between two tuples p1 and p2
    '''
    return Point(p1[0], p1[1]).distance(Point(p2[0], p2[1]))

def optimization(polygon, param_reg=1.0, param_smh=200.0, param_spacing=1.0, local=True):
    '''
    A pre-mature optimization for given polygon.
    Referencing to curve optimization detail from [Zhao, et al. 16] without spacing-preserving term
    '''
    # deal with nest polygon structures
    # space inefficient, but whatever...
    if local and type(polygon) is list:
        return [optimization(nest_polygon, param_reg, param_smh, param_spacing, local) for nest_polygon in polygon]
    
    # original coords
    m, n = get_xy(polygon, local)
    mn = np.concatenate((m, n))
    
    # variables to be optimized
    x = cp.Variable(m.shape)
    y = cp.Variable(n.shape)

    # penalty for magnitude of the perturbations, formulated as distance least squares
    x_reg_cost = cp.sum_squares(x - m)
    y_reg_cost = cp.sum_squares(y - n)
    
    # construct modified scalar for mid-point scheme
    coords = get_coord_list(polygon)
    
    u = []
    for i in range(m.shape[0] - 2):
        u_i = dist(coords[i], coords[i + 1]) / (dist(coords[i], coords[i + 1]) + dist(coords[i + 1], coords[i + 2]))
        u.append([u_i])
    u = np.matrix(u)
    
    # construct matrix L, a (n-2)-by-n matrix where n=m.shape, or the number of variables
    # it encodes scalars for calculating f_smooth
    L = []
    for i in range(m.shape[0] - 2):
        row_i = [0 for j in range(m.shape[0])]
        row_i[i] = 1 - u.item(i)
        row_i[i + 1] = -1
        row_i[i + 2] = u.item(i)
        L.append(row_i)
    L = np.matrix(L)
        
    # smoothness potential, formualted as L2 norm
    # note that we cannot explicitly write out the whole expression in matrix form
    # using x.T @ L.T will cause the cvxpy fails to realize the whole objective is actually convex
    # as it treats x.T and x as two different variable vectors 
    x_smh_ptnt = cp.sum_squares(L @ x)
    y_smh_ptnt = cp.sum_squares(L @ y)

    optimize = cp.Problem(cp.Minimize((x_reg_cost + y_reg_cost) * param_reg + (x_smh_ptnt + y_smh_ptnt) * param_smh))
    optimize.solve()
    
    points = []
    for i in range(len(x.value)):
        points.append((x.value[i][0], y.value[i][0]))

    # depending on what we optimize on, the output will be in different format
    if local:
        return Polygon(points)
    else:
        return points

'''
Applies optimization to a polygon
'''
def optimize_polygon(polygon, opt_reg=1, opt_smh=10, opt_spacing=0, samples=1):
    s = list(sample(polygon.exterior,samples).coords)
    
    # only run optimization on polygons that are large enough
    if len(s) > 5:
        ext = optimization(s, opt_reg, opt_smh, opt_spacing, False)

        ints = []

        for interior in polygon.interiors:
            i = list(sample(interior,samples).coords)
    
            if len(i) > 5:
                ints.append(optimization(i, opt_reg, opt_smh, opt_spacing, False))

        polygon = Polygon(ext, holes=ints)
    
    return polygon