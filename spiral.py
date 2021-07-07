'''
Generate a space-filling spiral path on an input polygon

@author ejbosia
'''

from shapely_utilities import distance_transform_diff, cut, cycle, self_intersections_binary, reverse

from shapely.geometry import Point, LineString, Polygon

from time import time

import numpy as np


'''
Spiral Class

This stores the components that make a spiral ~ a list of separate paths that can be formatted into a full path.
'''
class Spiral:

    '''
    Initialize the spiral ~ to do this, just need to find the start and end points of each contour
    '''
    def __init__(self, contours, distance):
        self.contours = self._generate_spiral(contours, distance)

    '''
    Generate the spiral
    '''
    def _generate_spiral(self, contours, distance):
    
        spiral_contours = []
        end = None

        # find the start and end point of each contour
        for contour in contours:

            # if there is a previous end point, find the start using this end point
            if not end is None:

                # set the start of the contour to the closest point to the end point
                start = contour.interpolate(contour.project(end))
                contour = cycle(contour, start)

            end = calculate_endpoint(contour, distance)

            # if there is a new valid end point, cut the contour and save the piece between the start and end point
            if not end is None:
                spiral_contours.append(cut(contour, contour.project(end))[0])

        return spiral_contours


    '''
    Output the path as a list of points
    '''
    def get_path(self):
        path = [c for contour in self.contours for c in contour.coords]
        
        # remove duplicates
        path = list(dict.fromkeys(path))

        return path

'''
Generate a list of Spirals from a list of polygons
'''
class SpiralGenerator:

    def __init__(self, polygons, distance, boundaries=0):
        self.polygons = polygons
        self.distance = distance
        self.boundaries = 0


    # create a list of Spirals from the polygons
    def generate(self):

        spirals = []

        for polygon in self.polygons:
            
            # get the isocontours
            contours = distance_transform_diff(polygon, self.distance)
            contours = self._flatten(contours)
            
            # initialize a spiral for each set of contours
            for c in contours:
                spirals.append(Spiral(c, self.distance))

        return spirals

    # flatten the output of distance_transform
    def _flatten(self, contours):
        
        format_list = []
        temp = []
            
        for c in contours:
            if type(c) is list:
                format_list.extend(self._flatten(c))
            else:
                temp.append(c)
        
        format_list.append(temp)       
        
        return format_list



'''
Find the endpoint guarenteed ~ avoids finding the wrong point in calculate point
'''
def calculate_endpoint(contour, radius):
    
    # reverse the contour coords to loop backwards through them
    points = contour.coords[::-1]

    start = Point(points[0])

    # find the first distance past the position (all previous will be before the position)
    for i, p in enumerate(points):
        
        dis = start.distance(Point(p))

        if dis > radius:
            index = i
            break
    else:
        return None

    # set the index correctly to match reverse
    i1 = index
    i0 = (index-1)

    # we know the intersection must be on this line, and there can only be one
    distance_ring = start.buffer(radius).exterior
    line = LineString(points[i0:i1+1])

    # the return of this must be a point
    point = distance_ring.intersection(line)
        
    return point


'''
Calculate a point a distance away from a position on the contour in a given direction
this is where the contour is rerouted to the next spiral
- contour: LineString input
- position: starting position to measure from
- radius: distance away from the starting point
- forward: direction along the contour to find the point
'''
def calculate_point(contour, position, radius, forward = True):
    
    # set the direction of the error
    direction = 1 if forward else -1
    
    # set the starting guess based on the direction
    error = direction * radius
    
    distance = position
    
    # save the start point for distance calculations
    start = contour.interpolate(position)
    
    # loop while the error is out of bounds 
    while abs(error) > 0.000001:
        
        distance += error
        
        # return None if the endpoints of the contour are reached
        if distance >= contour.length or distance <= 0:
            return None
        
        # get point
        point = contour.interpolate(distance)
        
        # calculate distance
        new_dis = point.distance(start)
        
        # calculate error
        error = direction * (radius - new_dis)/2
        
    return point


'''
Calculate a point a distance away from a position on the contour in a given direction
this is where the contour is rerouted to the next spiral
- contour: LineString input
- position: starting position to measure from
- radius: distance away from the starting point
- forward: direction along the contour to find the point
'''
def calculate_point_contour(contour, previous, radius):

    # pick the ending point
    point = calculate_point(contour, contour.length , radius, forward = False)
    
    if point is None:
        return point
    
    # cut the path at the midpoint
    temp, _ = cut(contour, contour.length/2)
    
    # if the distance from the point to contour is the radius, return the point
    if radius - point.distance(temp) < 0.000001:
        return point
    
    # else find a valid distance and binary search to find valid point
    distance = contour.project(point)
    
    while point.distance(temp) < radius:
        
        distance -= radius
        
        if distance < 0:
            return None
        
        point = contour.interpolate(distance)
        
    max_error = contour.length - distance
    
    error = max_error/2
    
    position = distance + error
    
    point = contour.interpolate(position)
    
    
    # binary search the distance ~ uses some arbitrary amount of iteration? ~ set to 10 rn
    for _ in range(10):
        
        error = error/2
        
        if point.distance(temp) < radius:
            position -= error
        else:
            position += error
            
        point = contour.interpolate(position)
        
    return point

'''
Pick a good start point for spiral generation
This should be a point that...
 - has a large angle difference
 - has a long flat line
'''
def generate_start_point(contour, index):

    # find the longest line segment in contour
    distances = []

    points = [Point(p) for p in contour.coords]

    p0 = points[-1]

    for p1 in points:
        distances.append(p1.distance(p0))
        p0 = p1

    # sort the distances
    di = np.argsort(distances)

    p0 = points[di[index]-1]

    # cycle the contour and return
    return cycle(contour, p0)


'''
Resolve self intersections in the linestring
'''
def remove_intersections(path):

    # convert the path into a linestring
    ls = LineString(path)

    # check if the linestring has any self intersections
    if ls.is_simple:
        return path

    # find the self intersections
    intersections = self_intersections_binary(ls)

    # reverse the linestring to set the center of the path to the 
    rls = reverse(ls)

    # sort the points by the projection distance from the center
    intersections.sort(key=rls.project)   
    
    while intersections:
        
        # get the starting point
        p = intersections[0]                

        # cut path at point, keep first part
        p1, p2 = cut(rls, rls.project(p))

        if len(p1.coords) < 3 or len(p2.coords) < 3:
            intersections.remove(p)
            continue

        # remove the cut point from each part
        p1 = LineString(p1.coords[:-1])
        p2 = LineString(p2.coords[1:])

        # find the distance from p1 and p2 to the cut point ~ should be one 0
        if p1.distance(p) < 0.000000001:
            p1,remainder = cut(p1, p1.project(p))
        else:
            remainder,p2 = cut(p2, p2.project(p))

        rls = LineString(list(p1.coords) + list(p2.coords))

        # remove the used point
        intersections.remove(p)
            
        # remove any points on the remainder path
        for test_p in intersections.copy():
            
            # set the epsilon distance to 1e-9 ~ this is "good enough" to be considered an intersection
            if test_p.distance(remainder) < 0.000000001:
                intersections.remove(test_p)

    # convert trimmed result back into the path
    path = list(reverse(rls).coords)   

    return path