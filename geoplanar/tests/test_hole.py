#!/usr/bin/env python3

import geopandas
from shapely.geometry import box

from geoplanar.hole import missing_interiors


class TestHole:
    def setup_method(self):
        p1 = box(0, 0, 10, 10)
        p2 = box(1, 1, 3, 3)
        p3 = box(7, 7, 9, 9)

        self.gdf = geopandas.GeoDataFrame(geometry=[p1, p2, p3])

    def test_missing_interiors(self):
        mi = missing_interiors(self.gdf)
        assert mi == [(0, 1), (0, 2)]
