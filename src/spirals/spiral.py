'''
Generate a space-filling spiral path on an input polygon

@author ejbosia
'''

from ..utilities.shapely_utilities import distance_transform_diff, cut, cycle, self_intersections_binary, reverse

from shapely.geometry import Point, LineString, Polygon

import numpy as np

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
Find the endpoint guarenteed ~ avoids finding the wrong point in calculate point
'''
def calculate_endpoint(contour, radius, forward = False):
    
    # set the direction of the error
    direction = 1 if forward else -1
    
    index = -1

    # reverse the contour coords to loop backwards through them
    points = contour.coords[::-1]

    start = Point(points[0])

    # find the first distance past the position (all previous will be before the position)
    for i, p in enumerate(points):
        
        dis = start.distance(Point(p))

        if dis > radius:
            index = i
            break
    
    # if no point was valid, then we return "None"
    if index == -1:
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
Generate a spiral path from an input family of contours
'''
def spiral_path(contour_family, distance, start_index=0):

    points = []

    if not contour_family:
        return points
    
    # set the start contour
    contour = contour_family[0]
    
    # set the starting point as start_index (arbitrary)
    # contour = LineString(list(contour.coords)[start_index:] + list(contour.coords)[:start_index])
    contour = generate_start_point(contour, start_index)

    # calculate the end point a distance away from the end of the contour
    end = calculate_endpoint(contour, distance)

    # if the end point was not found, return an empty list ~ contour is too small
    if end is None:
        return []
    
    # add the points before the reroute point to the path
    ls, _ = cut(contour, contour.project(end))                
    points.extend(ls.coords)
    
    # the previous contour is used to force the point away from acute angles
    previous = contour
    
    # loop through each "inner" contour
    for contour in contour_family[1:]:

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


'''
Create a cleaned spiral path with no duplicate points or self intersections
'''
def generate_path(contour_family, distance, start_index=0):

    # run the path algorithm until the path exterior is correct
    i = start_index
    done = False

    outer_ring = contour_family[0]

    while not done:

        # generate the spiral path
        path = spiral_path(contour_family, distance, i)

        if path:

             # remove any duplicate points in the path
            path = list(dict.fromkeys(path))

            start_length = LineString(path)

            # remove any self intersections in the path
            # path = remove_intersections(path)

            done = LineString(path).is_simple
            i += 1

        else:
            done = True

       
    return path


'''
Create a cleaned spiral path with no duplicate points or self intersections
'''
def generate_total_path(isocontours, distance):
    total_path = []
    contour_family = []
    
    # loop through each value in the result
    for branch in isocontours:
        if type(branch) is list:  
            total_path.extend(generate_total_path(branch, distance))
        else:
            contour_family.append(branch)

        path = generate_path(contour_family, distance)
    
    total_path.append(path)

    return total_path



'''
Generate the spiral fill
'''
def execute(polygons, distance, boundaries=0):

    total_path = []

    for polygon in polygons:
        isocontours = [polygon.exterior] + distance_transform_diff(polygon, distance) 

        if isocontours:

            path = generate_total_path(isocontours[boundaries:], distance)

            total_path.extend(path)

    return total_path