'''
GcodeWriter

The GcodeWriter takes in a array-like path of array-like points (2D or 3D) and converts into a gcode path
'''

from shapely.geometry import Point, LineString

class GcodeWriter:

    '''
    filename: file location to save the gcode
    extruder: true if the extruder should be enabled for printing
    x_offset: add this to every x coordinate
    y_offset: add this to every y coordinate
    z_offset: add this to clear the z position during rapid moves
    z_floor: used to calculate the up and down positions
    '''

    def __init__(self, filename=None, scale=1, extruder=False, x_offset=0, y_offset=0, z_offset=0):
        self.filename = filename
        self.extruder = extruder
        self.scale = scale
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.z_offset = z_offset

        self.coordinate = ['X','Y','Z']


    '''
    Convert a point into GCODE coordinates ~ assumes p is X,Y,Z in that order with Z optional
    '''
    def convert_point(self, p):
        return " ".join([self.coordinate[i] + str(value * self.scale) for i,value in enumerate(p)])


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
        return "G01 Z2.0;\n"


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


    '''
    Convert the path into printable code
    '''
    def convert_print(self, total_path, layer, height):

        current_layer = layer

        output = self.header()

        while current_layer < height:
            for path in total_path:
                
                # move to p0
                output += self.command_rapid(path[0])
                
                # pen down
                output += "G01 Z" + str(current_layer) + ";\n"
                
                # trace the path
                for p in path[1:]:
                    output += self.command_move(p)
                    
                # pen up
                output += "G01 Z" + str(current_layer + 2) + ";\n"
            
        # home machine
        output += "G28 X Y;\n"
                
        # write the code to a gcode file
        if not self.filename is None:
            f = open(self.filename, "w")
            f.write(output)
            f.close()
        
        # return the string (for debugging, not really needed)
        return output



    '''
    Convert the path into printable code
    '''
    def convert_supervase(self, path, layer=0.2, height=10):

        # super vase only works for length 1 paths
        assert len(path) == 1

        current_layer = layer / 2

        output = self.header()

        # move to p0
        output += self.command_rapid(path[0][0])

        # pen down
        output += "G01 Z" + str(current_layer) + ";\n"

        # calculate the total length of the path
        total_dis = LineString(path[0]).length

        debug_list = []

        while current_layer < height:

            p0 = path[0][0]
            z = current_layer

            output += self.command_move((p0[0],p0[1],z))
            debug_list.append((p0[0],p0[1],z))

            # trace the path
            for p in path[0][1:]:

                # add a fraction of the layer based on the difference of the layer
                z += Point(p0).distance(Point(p))/total_dis * layer

                output += self.command_move((p[0],p[1],z))
                debug_list.append((p[0],p[1],z))
            
            current_layer += layer

        # pen up
        output += "G01 Z" + str(current_layer + 2) + ";\n"
            
        # home machine
        output += "G28 X Y;\n"
                
        # write the code to a gcode file
        if not self.filename is None:
            f = open(self.filename, "w")
            f.write(output)
            f.close()
        
        # return the string (for debugging, not really needed)
        return debug_list





