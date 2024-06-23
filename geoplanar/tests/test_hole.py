#!/usr/bin/env python3

import geopandas
import numpy
from shapely.geometry import box

from geoplanar.hole import add_interiors, missing_interiors


class TestHole:
    def setup_method(self):
        p1 = box(0, 0, 10, 10)
        p2 = box(1, 1, 3, 3)
        p3 = box(7, 7, 9, 9)

        self.gdf = geopandas.GeoDataFrame(geometry=[p1, p2, p3])
        self.gdf_str = self.gdf.set_index(numpy.array(["foo", "bar", "baz"]))

    def test_missing_interiors(self):
        mi = missing_interiors(self.gdf)
        assert mi == [(0, 1), (0, 2)]

    def test_add_interiors(self):
        gdf1 = add_interiors(self.gdf, inplace=True)
        mi = missing_interiors(gdf1)
        assert mi == []

        gdf1 = add_interiors(self.gdf_str, inplace=True)
        mi = missing_interiors(gdf1)
        assert mi == []
