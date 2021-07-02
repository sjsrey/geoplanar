"""
GeoPlanar

A module for handling planar enforcement for polygon geoseries.
"""

from geoplanar.overlap import trim_overlaps, is_overlapping
from geoplanar.hole import holes, fill_holes
from geoplanar.planar import (planar_enforce, is_planar_enforced,
                              fix_npe_edges, insert_intersections,
                              non_planar_edges)
from geoplanar.valid import isvalid
