'''
Test different shapely conversions
'''

import src.utilities.shapely_conversion as SC

import os
import cv2

from shapely.geometry import Polygon

import pytest

def image_loader_generator():

    files = next(os.walk('test_images'))[2]

    for f in files:
        yield(cv2.imread(os.path.join('test_images',f), 0))


def test_generate_border_lines():

    # get the square boundaries    
    square = cv2.imread(os.path.join('test_images', 'test-002_square.png'), 0)

    # get the border lines
    borders = SC.generate_border_lines(square)

    assert len(borders) == 1
    assert len(borders[0][0]) == 4

    # get multiple boundaries
    multi = cv2.imread(os.path.join('test_images', 'test-003_multi.png'), 0)

    # get the border lines (should be 5 total, each with 4 sides)
    borders = SC.generate_border_lines(multi)
    assert len(borders) == 5
    assert all([len(b[0]) == 4 for b in borders])
    

def test_create_contour_families():

    # get multiple boundaries
    multi = cv2.imread(os.path.join('test_images', 'test-003_multi.png'), 0)

    # get the border lines (should be 5 total, each with 4 sides)
    borders = SC.generate_border_lines(multi)

    # get the polygons
    polygons = SC.create_contour_families(borders)

    assert len(polygons) == 5

    # get multiple boundaries
    heir = cv2.imread(os.path.join('test_images', 'test-005_heir.png'), 0)

    # get the border lines (should be 5 total, each with 4 sides)
    borders = SC.generate_border_lines(heir)

    # get the polygons
    polygons = SC.create_contour_families(borders)

    assert len(polygons) == 2

    total = 0
    # only one polygon should have a hole
    for p in polygons:
        total += len(p.interiors)

    assert total == 1


def test_convert():

    # test bad simplify value
    with pytest.raises(ValueError) as error:
        SC.convert(None, simplify=-1)

    assert error.value.args[0] == "SIMPLIFY MUST BE GEQ 0"
    assert error.type == ValueError

    for image in image_loader_generator():
        polygons1 = SC.convert(image)
        polygons2 = SC.convert(image, simplify=1)

        for p1, p2 in zip(polygons1, polygons2):
            assert len(p1.exterior.coords) >= len(p2.exterior.coords)
            assert abs(p1.area - p2.area) < 0.01*p1.area