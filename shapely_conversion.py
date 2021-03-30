'''
Convert input binary images into shapely polygons

@author ejbosia
'''

import cv2

from shapely.geometry import Polygon

'''
Convert an input binary image into a formatted list of contours with heirarch information
 - this returns all of the contours and heirarchy information
 - returns a list of tuples --> (list of points, heirarchy)
'''
def generate_border_lines(image, approximation = cv2.CHAIN_APPROX_SIMPLE):

    # cv2.RETR_CCOMP outputs parent-children relationships in the heirarchy
    contours,heirarchy = cv2.findContours(image, cv2.RETR_CCOMP, approximation)  

    contour_list = []

    for contour,heirarchy in zip(contours, heirarchy[0]):
        point_list = []
        for point in contour:
            point_list.append(tuple(point[0]))
            
        contour_list.append((point_list, heirarchy))

    return contour_list

'''
Get all of the children of the parent contour using heirarchy information
'''
def get_children(contour_list, parent_contour):

    child_list = []

    first_child_index = parent_contour[1][2]
    child = contour_list[first_child_index]
    child_list.append(child[0])


    # loop while there are more children
    while not child[1][0] == -1:
        next_child_index = child[1][0]
        child = contour_list[next_child_index]
        child_list.append(child[0])
    
    # return the list of children
    return child_list

'''
Convert formatted list of contours with heirarchy info into polygons
 - a shapely polygon has an exterior list of points, and a list of interiors (lists of points)
 - this uses the heirarchy info to find the interiors of an exterior polygon
'''
def create_contour_families(contour_list):

    family_list = []

    # find the first parent contour
    for contour in contour_list:
        
        # start with a parent contour
        if contour[1][3]==-1:

            # if there are no children, create an empty family with only the parent contour
            if contour[1][2] == -1:
                child_list = []
            # otherwise, find all of the children
            else:
                child_list = get_children(contour_list, contour)

            if len(contour[0]) > 2:
                family_list.append(Polygon(contour[0], holes=child_list))

    return family_list


'''
Convert an image into a list of shapely polygons.
 - use this function to perform all of the conversion steps
'''
def convert(image, approximation = cv2.CHAIN_APPROX_SIMPLE):
   
    contour_list = generate_border_lines(image, approximation)
    
    return create_contour_families(contour_list)