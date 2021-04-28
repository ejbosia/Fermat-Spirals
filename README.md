# Fermat-Spirals
Connected Fermat Spirals are a space filling curve that could be used for additive manufacturing. The algorithm is presented in this paper: https://dl.acm.org/doi/10.1145/2897824.2925958.

The goal of this project is to implement the algorithm as presented in the paper and ultimately use this algorithm to generate a fill pattern for 3D printing.


## Code Execution Instructions
The code can be executed either through the "Fermat Spiral Paper" Jupyter Notebook, or through **main.py** using the CLI.

### Command Line Interface
The code can be run with this command. Note the filename and distance are required inputs:

'''bash
python3 main.py filename distance
'''

There are optional commands that can be used to control the desired output of the program. They are listed below:

Mutually Exclusive (choose one):
 - -s: runs spiral path generation
 - -fs: runs fermat spiral path generation
 - -cfs: runs connected fermat spiral path generation

Optional Arguments:
 - -o: enables optimization
 - -p: displays plot of paths using matplotlib
 - -g "filename.gcode": writes gcode of output to input filename
 - -m: prints dictionary of calculated metrics of path

An example command that opens "picture.png" from the local directory, runs fermat spiral generation at distance = 2, uses optimization, displays a plot of the path, and outputs a gcode file to "temp.gcode" in the local directory.

'''bash
python3 main.py "picture.png" 2 -fs -o -p -g "temp.gcode"
'''

## Example Results:
Here is a plot of a CFS path of the wolf:

## References
Haisen Zhao, Fanglin Gu, Qi-Xing Huang, Jorge Garcia, Yong Chen, Changhe Tu, Bedrich Benes, Hao Zhang, Daniel Cohen-Or, and Baoquan Chen. 2016. Connected fermat spirals for layered fabrication. ACM Trans. Graph. 35, 4, Article 100 (July 2016), 10 pages. DOI:https://doi.org/10.1145/2897824.2925958
