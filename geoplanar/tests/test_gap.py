#!/usr/bin/env python3

import geopandas
import numpy
from numpy.testing import assert_equal
from shapely.geometry import Polygon, box
import pytest
from geoplanar import fill_gaps, gaps, snap


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

@pytest.mark.skipif(geopandas.__version__ != "1.0.0-alpha1", reason="requires geopandas alpha release")
class TestSnap:
    def setup_method(self):
        self.p1 = Polygon([[0, 0], [10,0], [10,10], [0,10]])
        self.p2 = Polygon([(11, 0), (21,0), (21,20), (11,20)])
        self.gdf = geopandas.GeoDataFrame(geometry=[self.p1, self.p2])
        self.gdf_crs = self.gdf.set_crs(3857)

    def test_snap_below_threshold(self):
        gdf1 = snap(self.gdf, 0.5)
        assert_equal(gdf1.area.values, numpy.array([100.0, 200.0]))

    def test_snap_above_threshold(self):
        gdf1 = snap(self.gdf, 1.1)
        assert_equal(gdf1.area.values, numpy.array([110.0, 200.0]))

    def test_snap_reverse_order(self):
        gdf = geopandas.GeoDataFrame(geometry=[self.p2, self.p1])
        gdf1 = snap(gdf, 1.1)
        assert_equal(gdf1.area.values, numpy.array([210.0, 100.0]))
