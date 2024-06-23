#!/usr/bin/env python3
import geopandas
import numpy
from libpysal.graph import Graph
from numpy.testing import assert_equal
from shapely.geometry import MultiPolygon, Polygon

import geoplanar


class TestPlanar:
    def setup_method(self):
        c1 = [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]
        p1 = Polygon(c1)
        c2 = [[10, 2], [20, 8], [20, 2], [10, 2]]
        p3 = Polygon([[21, 2], [21, 4], [23, 3]])

        p2 = MultiPolygon([Polygon(c2), p3])

        self.gdf = geopandas.GeoDataFrame(geometry=[p1, p2])
        self.gdf_str = self.gdf.set_index(numpy.array(["foo", "bar"]))

    def test_non_planar_edges(self):
        res = geoplanar.non_planar_edges(self.gdf)
        assert res.equals(Graph.from_dicts({0: [1], 1: [0]}))
        gdf1 = geoplanar.fix_npe_edges(self.gdf)
        assert_equal(
            gdf1.geometry[0].wkt, "POLYGON ((0 0, 0 10, 10 10, 10 2, 10 0, 0 0))"
        )

        res = geoplanar.non_planar_edges(self.gdf_str)
        assert res.equals(Graph.from_dicts({"foo": ["bar"], "bar": ["foo"]}))
        gdf1 = geoplanar.fix_npe_edges(self.gdf_str)
        assert_equal(
            gdf1.geometry.iloc[0].wkt, "POLYGON ((0 0, 0 10, 10 10, 10 2, 10 0, 0 0))"
        )
