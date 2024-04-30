#!/usr/bin/env python3

import geopandas
import numpy
from numpy.testing import assert_equal
from shapely.geometry import Polygon, box

from geoplanar import fill_gaps, gaps


class TestGap:
    def setup_method(self):
        self.p1 = box(0, 0, 10, 10)
        self.p2 = Polygon([(10, 10), (12, 8), (10, 6), (12, 4), (10, 2), (20, 5)])
        self.gdf = geopandas.GeoDataFrame(geometry=[self.p1, self.p2])
        self.gdf_crs = self.gdf.set_crs(3857)

    def test_gaps(self):
        h = gaps(self.gdf_crs)
        assert_equal(h.area.values, numpy.array([4.0, 4.0]))
        assert self.gdf_crs.crs.equals(h.crs)

    def test_fill_gaps(self):
        gdf1 = fill_gaps(self.gdf)
        assert_equal(gdf1.area.values, numpy.array([108.0, 32.0]))

    def test_fill_gaps_smallest(self):
        gdf1 = fill_gaps(self.gdf, largest=False)
        assert_equal(gdf1.area.values, numpy.array([100.0, 40.0]))

    def test_fill_gaps_none(self):
        gdf1 = fill_gaps(self.gdf, largest=None)
        assert_equal(gdf1.area.values, numpy.array([108.0, 32.0]))

    def test_fill_gaps_gaps_df(self):
        gaps_df = gaps(self.gdf).loc[[0]]
        filled = fill_gaps(self.gdf, gaps_df)
        assert_equal(filled.area, numpy.array([104, 32]))
