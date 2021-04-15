'''
Generate a space-filling spiral path on an input polygon

@author ejbosia
'''

from shapely_utilities import distance_transform, cut, cycle, self_intersections_binary, reverse

from shapely.geometry import Point, LineString, Polygon

from time import time

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
Generate a spiral path from an input family of contours
'''
def spiral_path(contour_family, distance):

    points = []

    if not contour_family:
        return points
    
    # set the start contour
    contour = contour_family[0].exterior
    
    # set the starting point as p0 (arbitrary)
    start = Point(contour.coords[0])
    
    # calculate the end point a distance away from the end of the contour
    end = calculate_point(contour, contour.length, distance, forward=False)
    
    # if the end point was not found, return an empty list ~ contour is too small
    if end is None:
        return []
    
    # add the points before the reroute point to the path
    ls, _ = cut(contour, contour.project(end))                
    points.extend(ls.coords)
    
    # the previous contour is used to force the point away from acute angles
    previous = contour
    
    # loop through each "inner" contour
    for polygon in contour_family[1:]:

        contour = polygon.exterior
        
        # get the next start point
        start = contour.interpolate(contour.project(end))
                
        # cycle so the start point is the coordinate at index 0
        contour = cycle(contour, start)
                
        # calculate the end point a distance away from the previous contour
        end = calculate_point_contour(contour, previous, distance)
                
        if end is None:
            break

        # add the points before the reroute point to the path
        ls, _ = cut(contour, contour.project(end))                
        points.extend(ls.coords)
        
        # set the previous to the processed contour so the next spiral generation can measure the distance from this
        previous = contour
        
    return points


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
        path1, remainder = cut(rls, rls.project(p))

        # remove the first point of the remainder 
        # two lines can intersect once, so the first line of the remainder cannot intersect with the path again
        remainder = LineString(remainder.coords[1:])

        # cut remainder at point, keep second part
        _, path2 = cut(remainder, remainder.project(p))

        # merge path1 and path2 (path1 and path2 are connected on the cut, so the path2 start point is trimmed)
        rls = LineString(list(path1.coords) + list(path2.coords)[1:])

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


'''
Create a cleaned spiral path with no duplicate points or self intersections
'''
def execute(contour_family, distance):


    # start = time()

    # generate the spiral path
    path = spiral_path(contour_family, distance)

    # print("\tSpiral", time()-start)

    # duplicates = time()
    # remove any duplicate points in the path
    path = list(dict.fromkeys(path))

    # print("\tDuplicates", time()-duplicates)

    # intersections = time()
    # remove any self intersections in the path
    path = remove_intersections(path)

    # print("\tRemove Intersections", time()-intersections)

    return path