#!/usr/bin/env python3

import geopandas
import numpy
from numpy.testing import assert_equal
from shapely.geometry import box

from geoplanar.overlap import (
    is_overlapping,
    merge_overlaps,
    merge_touching,
    trim_overlaps,
)


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

    def test_trim_overlaps_random(self):
        gdf1 = trim_overlaps(self.gdf, largest=None)
        assert_equal(gdf1.area.values, numpy.array([100.0, 4.0]))

    def test_trim_overlaps_multiple(self):
        gdf1 = trim_overlaps(self.gdf2, largest=False)
        assert_equal(gdf1.area.values, numpy.array([100.0, 100.0, 0.0]))

        gdf1 = trim_overlaps(self.gdf2, largest=None)
        assert_equal(gdf1.area.values, numpy.array([100.0, 100.0, 0.0]))

        gdf1 = trim_overlaps(self.gdf2)
        assert_equal(gdf1.area.values, numpy.array([96.0, 96.0, 8.0]))

    def test_merge_overlaps(self):
        gdf1 = merge_overlaps(self.gdf, 10, 0)
        assert_equal(gdf1.area.values, numpy.array([104]))

        gdf1 = merge_overlaps(self.gdf, 10, 1)
        assert_equal(gdf1.area.values, numpy.array([104]))

        gdf1 = merge_overlaps(self.gdf, 1, 0)
        assert_equal(gdf1.area.values, numpy.array([104]))

        gdf1 = merge_overlaps(self.gdf, 1, 1)
        assert_equal(gdf1.area.values, numpy.array([100, 8]))

    def test_merge_overlaps_multiple(self):
        gdf1 = merge_overlaps(self.gdf2, 10, 0)
        assert_equal(gdf1.area.values, numpy.array([200]))


class TestTouching:
    def setup_method(self):
        self.p1 = box(0, 0, 1, 1)
        self.p2 = box(1, 0, 11, 10)
        self.p3 = box(15, 0, 25, 10)
        self.p4 = box(0, 15, 1, 16)
        self.p5 = box(0.5, 1, 1, 8)
        self.gdf = geopandas.GeoDataFrame(
            geometry=[self.p1, self.p2, self.p3, self.p4, self.p5]
        )
        self.index = [0, 3]

    def test_merge_touching_largest(self):
        gdf1 = merge_touching(self.gdf, self.index, largest=True)
        assert_equal(gdf1.area.values, numpy.array([101, 100, 3.5]))

    def test_merge_touching_smallest(self):
        gdf2 = merge_touching(self.gdf, self.index, largest=False)
        assert_equal(gdf2.area.values, numpy.array([4.5, 100, 100]))

    def test_merge_touching_none(self):
        gdf3 = merge_touching(self.gdf, self.index, largest=None)
        assert_equal(gdf3.area.values, numpy.array([4.5, 100, 100]))
