'''
Methods for generating fermat spirals from input spirals

@author ejbosia
'''

import spiral as S
from spiral import calculate_point, calculate_point_contour

from shapely.geometry import Point, LineString

from shapely_utilities import cut, distance_transform


'''
Find the next endpoint in the path
 - this is the endpoint one "loop" around the contour
 - the next endpoint should be where the projection distance is greater than the distance away from the start
'''
def calculate_break(path, start, radius):

    dis = 0
    
    while dis <= radius:
        _,path = cut(path,radius)
        
        if path is None:
            return None
        
        dis = path.project(start)
    
    
    return path.interpolate(dis)


'''
Build the outer spiral of the fermat spiral
'''  
def outer_spiral(path, distance):
    
    path = LineString(path)
    
    # start at the first point in the contour
    start = Point(path.coords[0])
    
    spiral = []
    outer_pieces = []

    while True:        

        end = calculate_break(path, start, distance)
        # return if the end point is the end of the path
        if end is None or path.project(end) == path.length:   
            return spiral+list(path.coords), outer_pieces, True
        
        # get the reroute point away from the end towards start
        reroute = calculate_point(path, path.project(end), distance, forward=False)

        # cut the path at the reroute point
        p1,center = cut(path, path.project(reroute))

        # complete the reroute of the path at the end point
        center,p2 = cut(center, center.project(end))

        # get the inner point
        # - this is the point that is a distance farther than the projection distance
        start = calculate_break(p2, reroute, distance)

        # add these coordinates to the spirals
        spiral.extend(list(p1.coords))

        # if the length of the remaining path is where the next jump would be, break the loop
        if start is None or p2.project(start) == p2.length:
            return spiral + list(p2.coords)[::-1], outer_pieces, True
        
        # cut the inner contour at this point
        outer, inner = cut(p2, p2.project(start))
        outer_pieces.append(outer)

        # set the path to the inner part of the spiral
        path = inner
        


'''
Build the inner spiral of the fermat spiral using the pieces of the spiral
'''
def inner_spiral(outer_pieces, distance, center, path):    
    spiral = []
    
    if not outer_pieces:
        pass
    else:
        
        # reverse the outer pieces to go from inside to outside
        outer_pieces = outer_pieces[::-1]
        contour = outer_pieces[0]
        formatted_pieces = []
        
        # adjust the center position dependent on the type of center (center in or center out)
        if center:

            ls = LineString(path)
            
            temp = Point(contour.coords[-1])
            d = ls.project(temp)
            _,ls = cut(ls, d)

            end = calculate_point_contour(contour, ls, distance)

            if end is None:
                end = calculate_point(contour, contour.length, distance, False)

            contour,_ = cut(contour, contour.project(end))

            # self intersections possible ~ need to check somehow.... seems like it works ok-ish???           
            test_path = LineString(contour.coords[:-1])
            generated_path = LineString([contour.coords[-1], path[-1]])
                        
            if test_path.intersects(generated_path):
                int_point = test_path.intersection(generated_path)
                
                if int_point.type == "MultiPoint":
                    end = sorted(list(int_point), key=end.distance)[-1]
                else:
                    end = int_point
                    
                contour,_ = cut(contour, contour.project(end))

            formatted_pieces.append(contour)
        else:
            # center is outer_piece[0]            
            contour, _ = cut(contour, contour.project(Point(path[-1])))
            formatted_pieces.append(contour)
            
            ls = LineString(path)
            ls, _ = cut(ls, ls.project(Point(contour.coords[-1])))
            
            path = list(ls.coords)
            
            # self intersections possible ~ need to check somehow.... seems like it works ok-ish???           
            test_path = LineString(path[:-1])
            generated_path = LineString([contour.coords[-1], path[-1]])
            
            if test_path.intersects(generated_path):
                int_point = test_path.intersection(generated_path)
                
                if int_point.type == "MultiPoint":
                    end = sorted(list(int_point), key=end.distance)[0]
                else:
                    end = int_point
                    
                contour,_ = cut(contour, contour.project(end))
        

        for contour in outer_pieces[1:]:
            
            # find the point away from the endpoint of the current piece
            reroute = calculate_point(contour, contour.length, distance, forward=False)
            # remove the points after the reroute on the next contour
            contour, _ = cut(contour, contour.project(reroute))
            
            formatted_pieces.append(contour)
            
            
        # loop through the formatted pieces
        for i in range(len(formatted_pieces)-1):
            
            # collect the current and next piece
            c0 = formatted_pieces[i]
            c1 = formatted_pieces[i+1]
            
            # project the end of the formatted end piece of the next contour on the inner contour
            dis = c0.project(Point(c1.coords[-1]))
            
            # if the projection is the start point, do not cut
            if dis == 0:
                spiral.extend(list(c0.coords)[::-1])
            else:
                _, inner = cut(c0,  dis)
                spiral.extend(list(inner.coords)[::-1])
                
        
        # add the last piece
        spiral.extend(list(formatted_pieces[-1].coords)[::-1])
    
    # return path + spiral[::-1]
    return S.remove_intersections(path) + S.remove_intersections(spiral[::-1])[::-1]


'''
Convert a spiral path into a fermat path
'''
def convert_fermat(path,distance, debug=False):
    
    if path is None or not path:
        return []
    
    path, pieces, center = outer_spiral(path, distance)

    result = inner_spiral(pieces, distance, center, path)
    
    return result


'''
Connect root and branch fermat spirals
'''
def combine_paths(root, branches, dis):
        
    root_ls = LineString(root)
        
    # find the start and end points of the root
    for b in branches:

        if not b:
            continue
        
        start = b[0]
        end = b[-1]
        
        # project end onto the root
        end_cut_dis = root_ls.project(Point(end))
        
        point = root_ls.interpolate(end_cut_dis)

        int_buff = point.buffer(dis)

        # get the line within the buffer distance of the point
        possible_line = int_buff.intersection(root_ls)

        start_pt = None
        
        if possible_line.type == "LineString":
            start_pt = possible_line.interpolate(possible_line.project(Point(start)))
        else:
            for item in possible_line:

                if item.type == "LineString":
                    # need to use this check instead of intersects because intersects will return false for some reason
                    test = item.interpolate(item.project(point))

                    if test.almost_equals(point):
                        start_pt = item.interpolate(item.project(Point(start)))
                        break

        start_cut_dis = root_ls.project(start_pt)        

        # if the start is 0 
        if start_cut_dis == 0:

            # shift the end point away from the start
            new_end = calculate_point(root_ls, 0, dis, True)

            _,l2 = cut(root_ls, root_ls.project(new_end))
            new_list = [root_ls.coords[0]] + b + list(l2.coords)

        # if the end is at the start
        elif end_cut_dis == 0:

            new_end = calculate_point(root_ls, 0, dis, True)

            _,l2 = cut(root_ls, root_ls.project(new_end))
            new_list = [root_ls.coords[0]] + b[::-1] + list(l2.coords)
        
        # if the start is at the end
        elif start_cut_dis == root_ls.length:

            new_end = calculate_point(root_ls, root_ls.length, dis, False)

            l1,_ = cut(root_ls, root_ls.project(new_end))
            new_list = list(l1.coords) + b[::-1] + [root_ls.coords[-1]]

        # if the end is at the end
        elif end_cut_dis == root_ls.length:

            new_end = calculate_point(root_ls, root_ls.length, dis, False)

            l1,_ = cut(root_ls, root_ls.project(new_end))
            new_list =  list(l1.coords) + b + [root_ls.coords[-1]]       

        elif start_cut_dis < end_cut_dis:
            l1,_ = cut(root_ls, start_cut_dis)
            _,l2 = cut(root_ls, end_cut_dis)
            
            new_list = list(l1.coords) + b + list(l2.coords)
        else:
            l1,_ = cut(root_ls, end_cut_dis)
            _,l2 = cut(root_ls, start_cut_dis)
            
            new_list =  list(l1.coords) + b[::-1] + list(l2.coords)       
        
        root_ls = LineString(new_list)
        
    return list(root_ls.coords)



'''
Generate unconnected fermat path
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

    i=0
    done = False
    while not done:
        s_path = S.generate_path(contour_family, distance,start_index=i) 
        root = convert_fermat(s_path,distance)

        if not s_path:
            break
        i+=1
        ratio = (LineString(root).length / LineString(s_path).length)
        done = ratio > 0.95

        if not done:
            print(i, " - FS")

    total_path.append(root)

    return total_path

'''
Generate connected fermat path
'''
def generate_total_path_connected(isocontours, distance):
    
    branches = []

    contour_family = []

    # loop through each node or branch in the tree
    for node in isocontours:
        
        # if the result node is a branch, recursively call this function on it
        if type(node) is list:
            branches.append(generate_total_path_connected(node, distance))
        # if the result node is not a branch, add it to the contour family
        else:
            contour_family.append(node)
    
    i=0
    done = False
    while not done:
        s_path = S.generate_path(contour_family, distance,start_index=i)     
        root = convert_fermat(s_path,distance)
        if not s_path:
            break
        i+=1
        ratio = (LineString(root).length / LineString(s_path).length)
        done = ratio > 0.95
    
    # combine the root and the branches if the root exists
    if root:
        return combine_paths(root, branches, distance)
    else:
        return branches



def clean_connected(path):
    
    total_path = []
    rest = []
    
    for p in path:

        if not p:
            continue

        if type(p) == list:
            if type(p[0]) == tuple:
                total_path.append(p)
            else:
                total_path.extend(clean_connected(p))
        else:
            rest.append(p)
                
    total_path.append(rest)
    return total_path
                


def execute(polygons, distance, connected=False, boundaries=0):
    
    assert not boundaries < 0

    total_path = []

    for polygon in polygons:
        isocontours = [polygon] + distance_transform(polygon, -distance) 


        if connected:
            if isocontours:

                for isocontour in isocontours[0:boundaries]:
                    total_path.append(list(isocontour.exterior.coords))

                    for interior in isocontour.interiors:
                        total_path.append(list(interior.coords))

                total_path.append(generate_total_path_connected(isocontours[boundaries:], distance))
        else:
            if isocontours:
                total_path.extend(generate_total_path(isocontours, distance))


    # need to clean output of connected path
    if connected:
        total_path = clean_connected(total_path)

    return total_path
