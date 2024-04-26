#!/usr/bin/env python3

import geopandas
import numpy
from numpy.testing import assert_equal
from shapely.geometry import box

from geoplanar.overlap import is_overlapping, trim_overlaps


def test_is_overlapping():
    p1 = box(0, 0, 10, 10)
    p2 = box(8, 4, 12, 6)
    gdf = geopandas.GeoDataFrame(geometry=[p1, p2])
    assert is_overlapping(gdf)


def test_trim_overlaps():
    p1 = box(0, 0, 10, 10)
    p2 = box(8, 4, 12, 6)
    gdf = geopandas.GeoDataFrame(geometry=[p1, p2])
    gdf1 = trim_overlaps(gdf)
    assert_equal(gdf1.area.values, numpy.array([96.0, 8.0]))

    p1 = box(0, 0, 10, 10)
    p2 = box(8, 4, 12, 6)
    gdf = geopandas.GeoDataFrame(geometry=[p1, p2])
    gdf1 = trim_overlaps(gdf, largest=False)
    assert_equal(gdf1.area.values, numpy.array([100.0, 4.0]))

    p1 = box(0, 0, 10, 10)
    p2 = box(10, 0, 20, 10)
    p3 = box(8, 4, 12, 6)
    gdf = geopandas.GeoDataFrame(geometry=[p1, p2, p3])
    gdf1 = trim_overlaps(gdf, largest=False)
    assert_equal(gdf1.area.values, numpy.array([100.0, 100.0, 0.0]))

    p1 = box(0, 0, 10, 10)
    p2 = box(10, 0, 20, 10)
    p3 = box(8, 4, 12, 6)
    gdf = geopandas.GeoDataFrame(geometry=[p1, p2, p3])
    gdf1 = trim_overlaps(gdf)
    assert_equal(gdf1.area.values, numpy.array([96.0, 96.0, 8.0]))
