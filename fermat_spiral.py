'''
Methods for generating fermat spirals from input spirals

@author ejbosia
'''

import spiral as S
from spiral import calculate_point, calculate_point_contour

from shapely.geometry import Point, LineString

from shapely_utilities import cut


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
    
    
    return S.remove_intersections(path) + S.remove_intersections(spiral[::-1])[::-1]


'''
Convert a spiral path into a fermat path
'''
def convert_fermat(path,distance, debug=False):
    
    if path is None or not path:
        return []
    
    path, pieces, center = outer_spiral(path, distance)
    
    return inner_spiral(pieces, distance, center, path)


'''
Create a fermat path from input contours
'''
def fermat_path(contours, distance,debug=False):
    
    path = S.execute(contours, distance)
    
    if path:
        fermat = convert_fermat(path, distance,debug)
    else:
        fermat = path
    
    return fermat


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
                    if test == point:
                        start_pt = item.interpolate(item.project(Point(start)))
                        break

                
        start_cut_dis = root_ls.project(start_pt)        
                
        if start_cut_dis == 0:
            _,l2 = cut(root_ls, end_cut_dis)
            new_list = [root_ls.coords[0]] + b + list(l2.coords)
        elif end_cut_dis == 0:
            _,l2 = cut(root_ls, start_cut_dis)
            new_list = [root_ls.coords[0]] + b[::-1] + list(l2.coords)
        
        elif start_cut_dis == root_ls.length:
            l1,_ = cut(root_ls, end_cut_dis)
            new_list = list(l1.coords) + b + [root_ls.coords[-1]]

        elif end_cut_dis == root_ls.length:
            l1,_ = cut(root_ls, start_cut_dis)
            new_list =  list(l1.coords) + b[::-1] + [root_ls.coords[-1]]       

        
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