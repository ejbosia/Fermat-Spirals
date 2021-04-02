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
    '''

    def __init__(self, filename=None, extruder=False, x_offset=0, y_offset=0, z_offset=5):
        self.filename = filename
        self.extruder = extruder
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.z_offset = z_offset


    # move the drawbot to a point
    def command_move(self, p):
        return "G01 X" + str(p[0]+self.x_offset) + " Y" + str(p[1]+self.y_offset) + ";\n"

    def command_rapid(self,p):
        return "G00 X" + str(p[0]+self.x_offset) + " Y" + str(p[1]+self.y_offset) + ";\n"

    # move the pen up (drawbot specific)
    def command_down(self):
        return "G01 Z0.0\n"

    # move the pen down (drawbot specific)
    def command_up(self):
        return "G01 Z" + str(self.z_offset) + ";\n"

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

    # input gcode which is \n separated, output a line plot
    # this is assuming all commands are XY, or Z
    def plot_gcode(self, gcode, debug=True, show=True, image=False, startstop=True, scale=True):
        commands = gcode.split('\n')

        X = [[]]
        Y = [[]]

        Z_down = []
        Z_up = []

        pen_down = False
        prev_x = 0
        prev_y = 0


        for c in commands:
            c = c.strip(';')
            if debug:
                print(c)
            if "Z8" in c:
                Z_down.append(np.array([prev_x, prev_y]))
                X.append([prev_x])
                Y.append([prev_y])
                pen_down=True

            if "G28" in c:
                continue
            elif "X" in c or "Y" in c:
                if pen_down:
                    if scale:
                        X[-1].append(float(c.split("X")[1].split(" ")[0]))
                        Y[-1].append(float(c.split("Y")[1].split(" ")[0]))
                    else:
                        X[-1].append(float(c.split("X")[1].split(" ")[0]))
                        Y[-1].append(float(c.split("Y")[1].split(" ")[0]))
                if scale:
                    prev_x = float(c.split("X")[1].split(" ")[0])
                    prev_y = float(c.split("Y")[1].split(" ")[0])
                else:
                    prev_x = float(c.split("X")[1].split(" ")[0])
                    prev_y = float(c.split("Y")[1].split(" ")[0])

            if not ("Z8" in c) and "Z" in c:
                try:
                    pen_down = False
                    Z_up.append(np.array([prev_x, prev_y]))
                except IndexError:
                    continue
            if c == "" and debug:
                print("HAHAHA")
        
        for i, temp in enumerate(X):
            pyplot.plot(X[i], Y[i], linewidth=0.2)

        Z_down = np.array(Z_down).transpose()
        Z_up = np.array(Z_up).transpose()




        if debug:
            print(Z_down)

        if startstop:
            pyplot.scatter(x=Z_down[0], y=Z_down[1], c="blue", s=50)
            pyplot.scatter(x=Z_up[0], y=Z_up[1], c='red', s=10)

        try:
            pyplot.imshow(image.transpose(),'gray')
        except:
            pass
        if show:
            pyplot.show()
