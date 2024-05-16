#!/usr/bin/env python3

import geopandas
import numpy
from numpy.testing import assert_equal
from shapely.geometry import box

from geoplanar.overlap import is_overlapping, trim_overlaps


class TestOverlap:
    def setup_method(self):
        self.p1 = box(0, 0, 10, 10)
        self.p2 = box(8, 4, 12, 6)
        self.p3 = box(10, 0, 20, 10)
        self.gdf = geopandas.GeoDataFrame(geometry=[self.p1, self.p2])
        self.gdf2 = geopandas.GeoDataFrame(geometry=[self.p1, self.p3, self.p2])

    def test_is_overlapping(self):
        assert is_overlapping(self.gdf)

    def test_trim_overlaps(self):
        gdf1 = trim_overlaps(self.gdf)
        assert_equal(gdf1.area.values, numpy.array([96.0, 8.0]))

    def test_trim_overlaps_smallest(self):
        gdf1 = trim_overlaps(self.gdf, largest=False)
        assert_equal(gdf1.area.values, numpy.array([100.0, 4.0]))

    def test_trim_overlaps_smallest(self):
        gdf1 = trim_overlaps(self.gdf, largest=None)
        assert_equal(gdf1.area.values, numpy.array([100.0, 4.0]))

    def test_trim_overlaps_multiple(self):
        gdf1 = trim_overlaps(self.gdf2, largest=False)
        assert_equal(gdf1.area.values, numpy.array([100.0, 100.0, 0.0]))

        gdf1 = trim_overlaps(self.gdf2, largest=None)
        assert_equal(gdf1.area.values, numpy.array([100.0, 100.0, 0.0]))

        gdf1 = trim_overlaps(self.gdf2)
        assert_equal(gdf1.area.values, numpy.array([96.0, 96.0, 8.0]))
