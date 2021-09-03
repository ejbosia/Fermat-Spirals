'''
This is a cli for the spiral generation
'''



import argparse

parser = argparse.ArgumentParser()

parser.add_argument("filename", help="path to image file", type=str)
parser.add_argument("distance", help="line thickness", type=float)

group = parser.add_mutually_exclusive_group()
group.add_argument("-s", "--spiral", action='store_true')
group.add_argument("-fs", "--fermat", action='store_true')
group.add_argument("-cfs", "--connected_fermat", action='store_true')

parser.add_argument("-o","--optimize", help="enable polygon optimization", action='store_true')
parser.add_argument("-p", "--plot", help="enable plotting", action='store_true')
parser.add_argument("-g", "--gcode", help="enable output", type=str)
parser.add_argument("-m", "--metrics", help="enable metrics", action='store_true')

import cv2
from matplotlib import pyplot

import os

# import utility functions
from shapely_conversion import convert
from shapely_utilities import *

# import spiral generation
import patterns.spirals as S
import patterns.spirals.cfs.fermat_spiral as FS

# add-on modules
from drawbot.metrics import Metrics
from drawbot.gcode import GcodeWriter



'''
Plot a single path
'''
def plot_path(path, color=None):
    
    X = []
    Y = []

    for p in path:
        X.append(p[0])
        Y.append(p[1])
        
    pyplot.plot(X,Y,c=color)

'''
Plot a list of paths
'''
def plot_recursive_path(total_path, color=None, endpoints=False, intersections=False):
    
    rest = []
    
    for path in total_path:
        
        if type(path) is list:
            plot_path(path, color)
            if intersections:
                for i in self_intersections_binary(LineString(path)):
                    pyplot.scatter(i.x,i.y, c='red')
        else:
            rest.append(path)
            
    plot_path(rest, color)
    pyplot.gca().invert_yaxis()



def main():
    
    args = parser.parse_args()

    filename = args.filename
    distance = args.distance

    assert distance > 0

    # read the image
    image = cv2.imread(filename,0)
    assert not image is None
    
    polygons = convert(image, approximation = cv2.CHAIN_APPROX_SIMPLE, optimize=args.optimize, simplify=1)

    path_type = ""

    # determine which path to create
    if args.spiral:
        results = S.execute(polygons, distance)
        path_type = "S"
    elif args.fermat:
        results = FS.execute(polygons, distance, connected=False)
        path_type = "FS"
    elif args.connected_fermat:
        results = FS.execute(polygons, distance, connected=True)
        path_type = "CFS"
    else:
        raise NotImplementedError("SPIRAL TYPE NOT INPUT")


    if args.plot:
        plot_recursive_path(results)
        pyplot.show()

    
    if not args.gcode is None:
        assert args.gcode.split('.')[-1] == 'gcode'
        gc = GcodeWriter(filename=args.gcode, scale = 0.1)
        gc.convert(results)
    

    if args.metrics:
        m = Metrics(segments=True, commands=True, curvature=False, underfill=True, overfill=True)
        print(m.measure(results, os.path.basename(filename), path_type, distance, polygons))


if __name__ == "__main__":
    main()