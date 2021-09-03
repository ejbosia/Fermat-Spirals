'''

'''

import src.utilities.shapely_utilities as SU

from shapely.geometry import LineString, Point

'''
Create a list of linestrings for testing
'''
def generate_linestrings():
    pass



def test_distance_transform():
    pass

'''
Distance transform without changing holes
'''
def test_distance_transform_diff():
    pass

# not testing plotting functions

'''
Cut a linestring at a specified distance. This always returns at least one linestring and a None, or two linestrings
'''
def test_cut():

    # create a linestring
    ls = LineString([(0,0),(10,0),(10,10),(20,10)])

    # test a normal cut
    start, end = SU.cut(ls, 15)

    assert start.length == 15
    assert end.length == ls.length - 15
    assert start.coords[-1] == end.coords[0]

    # test cutting on the start
    start, end = SU.cut(ls, 0)
    assert start is None
    assert end == ls

    # test cutting on the end
    start, end = SU.cut(ls, ls.length)
    assert start == ls
    assert end is None

    # test cutting a negative distance
    start, end = SU.cut(ls,-1)
    assert start is None
    assert end == ls

    # test cutting farther than the length
    start, end = SU.cut(ls, ls.length+1)
    assert start == ls
    assert end is None



'''
Reformat the linestring so position 0 is the start point. This may involve inserting a new point into the contour.
'''
def test_cycle():
    
    # create a linestring
    ls = LineString([(0,0), (10,0), (10,10), (0,10)])

    # test normal cycle
    output = SU.cycle(ls, 15)
    assert output.length == ls.length
    assert output.coords[0] == list(ls.interpolate(15))

    # test cycle past end of linestring (similar to x rotations + some distance)
    output = SU.cycle(ls, ls.length+15)
    assert output.length == ls.length
    assert output.coords[0] == list(ls.interpolate(15))

    # test negative cycle ()
    output = SU.cycle(ls, -15)
    assert output.length == ls.length
    assert output.coords[0] == list(ls.interpolate(ls.length-15))

    # test cycle on start (does nothing)
    assert ls == SU.cycle(ls, 0)

    # test cycle on end (does nothing)
    assert ls == SU.cycle(ls, ls.length)



'''
Find any self intersections in the input linestring
'''
def test_self_intersections():
    pass


'''
Find any self intersections in the input linestring using binary search like recursion
'''
def test_self_intersections_binary():
    pass


'''
Reverse a input linestring ~ this is helpful for projection when the distance is ambiguous (intersections)
'''
def test_reverse():
    ls = LineString([(0,0),(10,0),(10,10),(20,10)])
    coords = ls.coords

    assert ls.coords[::-1] == list(SU.reverse(ls).coords)


'''
Merge two linestrings
'''
def test_merge():
    ls = LineString([(0,0),(10,0),(10,10),(20,10)])
    
    start,end = SU.cut(ls, 15)

    output = SU.merge(start, end)

    assert output.length == ls.length
    assert output.coords[0] == ls.coords[0]
    assert output.coords[-1] == ls.coords[-1]


'''
Evenly sample the linestring ~ this returns a list of points
'''
def test_sample():
    
    ls = LineString([(0,0),(10,0),(10,10),(20,10)])

    assert len(ls.coords) == 4

    # check the sample distances
    points = SU.sample(ls, 1)
    p0 = None
    for p1 in points.coords:
        p1 = Point(p1)
        if not p0 is None:
            assert p1.distance(p0) == 1.0
        p0 = Point(p1)

    assert len(points.coords) == 30
    
    # check the start point is included in the sample
    assert points.coords[0] == ls.coords[0]


'''
Create a virtual boundary around a polygon ~ returns the exterior and a list of interiors
'''
def test_virtual_boundary():
    pass