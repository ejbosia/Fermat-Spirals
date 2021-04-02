'''
Utility functions to use with Shapely geometry objects

@author ejbosia
'''


from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import CAP_STYLE, JOIN_STYLE

from matplotlib import pyplot

'''
Recursively run the distance transform on the input polygon
- if result is empty, terminate with empty list
- if result is Polygon, add current Polygon
- if result is MultiPolygon, run for each Polygon in the MultiPolygon
'''
def distance_transform(polygon, distance):
        
    t = polygon.buffer(distance, cap_style = CAP_STYLE.flat, join_style = JOIN_STYLE.mitre)
    
    # if t is empty, return the empty list
    if not t:
        return []
        
    result = []

    # MultiPolygons are the result of concave shapes ~ distance transform creates multiple polygons
    if t.type == "MultiPolygon":
        for p in t:
            result.append([p])
            result[-1].extend(distance_transform(p, distance))
    else:
        result.append(t)
        result.extend(distance_transform(t, distance))
        
    return result

'''
Plot all of the contours of an input polygon
'''
def plot_poly(polygon):
    pyplot.plot(*polygon.exterior.xy)
    
    for i in polygon.interiors:
        pyplot.plot(*i.xy)


'''
Plot all of the contours in the result of a distance transform
'''
def plot_contours(result):
    for p in result:
        if type(p) is list:
            plot_contours(p)
        else:
            plot_poly(p)


'''
Cut a linestring at a specified distance. This always returns at least one linestring and a None, or two linestrings
'''
def cut(line, distance):
    # Cuts a line in two at a distance from its starting point
    if distance <= 0.0:
        return [None, LineString(line)]
    elif distance >= line.length:
        return [LineString(line), None]
    
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [
                LineString(coords[:i+1]),
                LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                LineString(coords[:i] + [(cp.x, cp.y)]),
                LineString([(cp.x, cp.y)] + coords[i:])]
    # this is between the last point
    # this is to catch for linear rings (last point projection is 0)
    cp = line.interpolate(distance)
    return [
        LineString(coords[:-1] + [(cp.x, cp.y)]),
        LineString([(cp.x, cp.y)] + [coords[-1]])]


'''
Reformat the linestring so position 0 is the start point. This may involve inserting a new point into the contour.
'''
def cycle(contour, point):
    
    # find the point projection on the contour
    proj = contour.project(point)
    
    # cut the contour at the projection distance
    result = cut(contour, proj)
    
    if result[0] is None:
        points = result[1]
    elif result[1] is None:
        points = result[0]
    else:
        [ls1,ls2] = result
        points = list(ls2.coords) + list(ls1.coords)

    return LineString(points) 


'''
Find any self intersections in the input linestring
'''
def self_intersections(ls):
    
    intersection_points = []
    
    for i in range(len(ls.coords)-3):
        
        p0 = ls.coords[i]
        p1 = ls.coords[i+1]
    
        remaining_path = LineString(ls.coords[i+2:])
        test = LineString([p0,p1])
        
        # check for intersection only with the linestring coords 2 past the start (the next line cannot intersect with the current line)
        if test.intersects(remaining_path):
            
            intersections = test.intersection(remaining_path)
            
            if intersections.type == "Point":
                intersection_points.append(intersections)
            else:
                for p in intersections:
                    intersection_points.append(p)

    return intersection_points


'''
Find any self intersections in the input linestring using binary search like recursion
'''
def self_intersections_binary(ls):
    
    intersection_points = []

    pivot = int(len(ls.coords)/2)

    ls1_coords = ls.coords[:pivot]
    ls2_coords = ls.coords[pivot:]

    ls1 = LineString(ls1_coords) if len(ls1_coords) > 1 else LineString()
    ls2 = LineString(ls2_coords) if len(ls1_coords) > 1 else LineString()

    s0 = ls.is_simple
    s1 = ls1.is_simple
    s2 = ls2.is_simple

    # if s0 is complex, but its bisects are simple, run the normal self intersection algorithm on s0
    if not s0 and s1 and s2:
        return self_intersections(ls)
    if not s1:
       intersection_points.extend(self_intersections_binary(ls1))
    if not s2:
       intersection_points.extend(self_intersections_binary(ls2))

    return intersection_points

'''
Reverse a input linestring ~ this is helpful for projection when the distance is ambiguous (intersections)
'''
def reverse(ls):
    return LineString(ls.coords[::-1])


'''
Merge two linestrings
'''
def merge(ls1, ls2):
    return LineString(ls1.coords + ls2.coords)


'''
Evenly sample the linestring ~ this returns a list of points
'''
def sample(ls, distance):
    
    pos = 0
    
    points = []
    
    while pos < ls.length:
        points.append(ls.interpolate(pos))
        
        pos += distance
        
    return LineString(points)


'''
Generate the curvature of each vertex on a linestring. The endpoints are set to ??? ~ this returns a list of curvatures of size equal to the number of vertices
'''
def curvature(ls):
    raise NotImplementedError("Curvature calculations has not been implemented yet")



'''
Adaptively sample the linestring based on the curvature of each vertex ~ this returns a new list of points
'''
def adaptive_sample(ls, K=1):
    raise NotImplementedError("Adaptive sampling has not been implemented")
