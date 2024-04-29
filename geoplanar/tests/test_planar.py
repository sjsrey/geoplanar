#!/usr/bin/env python3

from collections import defaultdict

import geopandas
from numpy.testing import assert_equal
from shapely.geometry import MultiPolygon, Polygon

import geoplanar


def setup():
    c1 = [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]
    p1 = Polygon(c1)
    c2 = [[10, 2], [20, 8], [20, 2], [10, 2]]
    p3 = Polygon([[21, 2], [21, 4], [23, 3]])

    # p2 = Polygon(c2)
    p2 = MultiPolygon([Polygon(c2), p3])

    gdf = geopandas.GeoDataFrame(geometry=[p1, p2])

    return gdf


def test_non_planar_edges():
    gdf = setup()
    # res = geoplanar.non_planar_edges(gdf)
    # assert_equal(res, defaultdict(set, {0: {1}}))
    gdf1 = geoplanar.fix_npe_edges(gdf)
    assert_equal(gdf1.geometry[0].wkt, "POLYGON ((0 0, 0 10, 10 10, 10 2, 10 0, 0 0))")
