'''
Take in a path and extract different metrics from the path
'''

try:
    from numba import jit
except ModuleNotFoundError:
    print("INSTALL NUMBA!")

import numpy as np

class Metrics:

    def __init__(self, segments=True, commands=True, curvature=True, fill=False):

        self.segments = segments
        self.commands = commands
        self.curvature = curvature
        self.fill = fill


    '''
    Count the number of commands needed to run the total path
    '''
    def measure_commands(self, total_path):

        commands = 0

        for path in total_path:
            commands += len(path)

        return commands


    '''
    Get the neighbor indices
    '''
    @jit(nopython=True)
    def neighbors(self, i1, length):
        
        i0 = i1-1 if i1 != 0 else length-1
        i2 = i1+1 if i1+1 != length else 0

        return i0,i1,i2


    '''
    Calculate average angle change of the path
    '''
    @jit(nopython=True)
    def _path_curvature(self, path):      
        
        sharpness = 0

        for i1 in range(len(path)):
            
            i0,i1,i2 = self.neighbors(i1, len(path))
            
            p0 = path[i0]
            p1 = path[i1]
            p2 = path[i2]
                    
            a0 = np.arctan2(p1[1]-p0[1], p1[0]-p0[0])
            a2 = np.arctan2(p2[1]-p1[1], p2[0]-p1[0])

            # get the angle change
            da = a2-a0
            
            sharpness += abs(da)
            
        return sharpness

    '''
    Get the total angle change. This should be directly comparable between paths
    '''
    def measure_curvature(self, total_path):

        sharpness = 0

        for path in total_path:
            sharpness += self._path_curvature(np.array(path))

        return sharpness


    '''
    Return a dictionary of measurements. Unused measurements are returned as np.Nan
    '''
    def measure(self, total_path, method, distance):

        assert type(distance) is float or type(distance) is int

        measurements = {
            "Method": method,
            "Distance": distance,
            "Segments": np.nan,
            "Commands": np.nan,
            "Curvature": np.nan,
            "Fill": np.nan,
        }

        if self.segments:
            measurements["Segments"] = len(total_path)
        if self.commands: 
            measurements["Commands"] = self.measure_commands(total_path)
        if self.curvature:
            raise NotImplementedError
        if self.fill:
            raise NotImplementedError






