'''
GcodeWriter

The GcodeWriter takes in a array-like path of array-like points (2D or 3D) and converts into a gcode path
'''

from matplotlib import pyplot
import numpy as np

class GcodeWriter:

    '''
    filename: file location to save the gcode
    extruder: true if the extruder should be enabled for printing
    x_offset: add this to every x coordinate
    y_offset: add this to every y coordinate
    z_offset: add this to clear the z position during rapid moves
    z_floor: used to calculate the up and down positions
    '''

    def __init__(self, filename=None, extruder=False, x_offset=0, y_offset=0, z_offset=0):
        self.filename = filename
        self.extruder = extruder
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.z_offset = z_offset

        self.coordinate = ['X','Y','Z']


    '''
    Convert a point into GCODE coordinates ~ assumes p is X,Y,Z in that order with Z optional
    '''
    def convert_point(self, p):
        return " ".join([self.coordinate[i] + str(value) for i,value in enumerate(p)])


    '''
    Normal move to point
    '''
    def command_move(self, p):
        return "G01 " + self.convert_point(p) + ";\n"

    
    '''
    Rapid move to point
    '''
    def command_rapid(self,p):
        return "G00 " + self.convert_point(p) + ";\n"



    # move the pen up (drawbot specific)
    def command_down(self):
        return "G01 Z8.0\n"


    # move the pen down (drawbot specific)
    def command_up(self):
        return "G01 Z0.5;\n"


    '''
    Build the header for the GCODE file
    '''
    def header(self):

        # home the printer
        output = "G28 Z;\n"
        output += self.command_up()
        output += "G28 X Y;\n\n"
        
        return output


    '''
    Convert the total path into 
    '''
    def convert(self, total_path): 
        
        output = self.header()

        # loop through each path
        for path in total_path:
            
            # move to p0
            output += self.command_rapid(path[0])
            
            # pen down
            output += self.command_down()
            
            # trace the path
            for p in path[1:]:
                output += self.command_move(p)
                
            # pen up
            output += self.command_up()
        
        # home machine
        output += "G28;\n"
                
        # write the code to a gcode file
        if not self.filename is None:
            f = open(self.filename, "w")
            f.write(output)
            f.close()
        
        # return the string (for debugging, not really needed)
        return output
