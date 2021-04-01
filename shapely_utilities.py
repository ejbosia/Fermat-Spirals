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
Evenly sample the linestring ~ this returns a list of points
'''
def sample(ls, distance):
    
    pos = 0
    
    points = []
    
    while pos < ls.length:
        points.append(ls.interpolate(pos))
        
        pos += distance
        
    return points 