import pytest

from src.spirals.spiral import Spiral, SpiralGenerator


# returns a list of polygons from test images
def generate_polygons():
    pass


def test_generator_creation():
    
    polygons = generate_polygons()

    # test empty polygons
    with pytest.raises(ValueError):
        SpiralGenerator([],1)

    # test low distance values
    with pytest.raises(ValueError):
        SpiralGenerator(polygons,0)
    with pytest.raises(ValueError):
        SpiralGenerator(polygons,-1)

def test_spiral():
    pass
