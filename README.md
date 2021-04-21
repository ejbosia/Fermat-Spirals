# Fermat-Spirals
Connected Fermat Spirals are a space filling curve that could be used for additive manufacturing. The algorithm is presented in this paper: https://dl.acm.org/doi/10.1145/2897824.2925958.

The goal of this project is to implement the algorithm as presented in the paper and ultimately use this algorithm to generate a fill pattern for 3D printing.

##Example Results:
Here is a plot of a proposed CFS path. The color change represents a gradual change in height of the print head. This mimics "vase" or "spiralize" mode on 3D printers. Theoretically, this could allow for 3D printing simple objects without retractions (like the walls of a planter).

![image](https://user-images.githubusercontent.com/17884767/115495450-a62f0d80-a235-11eb-8214-6e4e1e69e656.png)

## References
Haisen Zhao, Fanglin Gu, Qi-Xing Huang, Jorge Garcia, Yong Chen, Changhe Tu, Bedrich Benes, Hao Zhang, Daniel Cohen-Or, and Baoquan Chen. 2016. Connected fermat spirals for layered fabrication. ACM Trans. Graph. 35, 4, Article 100 (July 2016), 10 pages. DOI:https://doi.org/10.1145/2897824.2925958
