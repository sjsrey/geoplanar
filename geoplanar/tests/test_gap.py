#!/usr/bin/env python3

import pytest
import geopandas
from shapely.geometry import box, Polygon
from geoplanar.gap import gaps, fill_gaps
import numpy
from numpy.testing import assert_equal


def setup():
    p1 = box(0,0,10,10)
    p2 = box(1,1, 3,3)
    p3 = box(7,7, 9,9)
    gdf = geopandas.GeoDataFrame(geometry=[p1,p2,p3])
    return gdf


def test_gaps():
    p1 = box(0,0,10,10)
    p2 = Polygon([(10,10), (12,8), (10,6), (12,4), (10,2), (20,5)])
    gdf = geopandas.GeoDataFrame(geometry=[p1,p2])
    h = gaps(gdf)
    assert_equal(h.area.values, numpy.array([4.,4.]))


def test_fill_gaps():
    p1 = box(0,0,10,10)
    p2 = Polygon([(10,10), (12,8), (10,6), (12,4), (10,2), (20,5)])
    gdf = geopandas.GeoDataFrame(geometry=[p1,p2])
    gdf1 = fill_gaps(gdf)
    assert_equal(gdf1.area.values, numpy.array([108.,32.]))
    gdf1 = fill_gaps(gdf, largest=False)
    assert_equal(gdf1.area.values, numpy.array([100.,40.]))
    p1 = box(0,0,10,10)
    p2 = Polygon([(10,10), (12,8), (10,6), (12,4), (10,2), (20,5)])
    gdf = geopandas.GeoDataFrame(geometry=[p1,p2])
    gaps_df = gaps(gdf).loc[[2]]
    filled = fill_gaps(gdf, gaps_df)
    assert_equal(filled.area, numpy.array([104, 32]))
