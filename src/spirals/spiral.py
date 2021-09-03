'''
Generate a space-filling spiral path on an input polygon

@author ejbosia
'''

from src.utilities.shapely_utilities import distance_transform, cut, cycle, self_intersections_binary, reverse
from src.spirals.fill_pattern import FillPattern

from shapely.geometry import Point, LineString, Polygon

import numpy as np

'''
Spiral Class

This stores the components that make a spiral ~ a list of separate paths that can be formatted into a full path.
'''
class Spiral(FillPattern):

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
                contour = cycle(contour, contour.project(end))

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

        if not polygons:
            raise ValueError("POLYGONS IS EMPTY")
        if distance <= 0:
            raise ValueError("DISTANCE IS 0 OR NEGATIVE")

        self.polygons = polygons
        self.distance = distance
        self.boundaries = 0


    # create a list of Spirals from the polygons
    def generate(self):

        spirals = []

        for polygon in self.polygons:
            
            # get the isocontours
            contours = distance_transform(polygon, self.distance)
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


def calculate_point():
    pass

def calculate_point_contour():
    pass