#!/usr/bin/env python3

import pytest
import geopandas
from shapely.geometry import box, Polygon
from geoplanar.hole import missing_interiors
import numpy
from numpy.testing import assert_equal


def setup():
    p1 = box(0,0,10,10)
    p2 = box(1,1, 3,3)
    p3 = box(7,7, 9,9)

    gdf = geopandas.GeoDataFrame(geometry=[p1,p2,p3])
    return gdf


def test_missing_interiors():
    gdf = setup()
    mi = missing_interiors(gdf)
    assert (mi == [(0, 1), (0, 2)])

