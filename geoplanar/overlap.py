#!/usr/bin/env python3
import geopandas
from packaging.version import Version

__all__ = ["overlaps", "trim_overlaps", "is_overlapping"]

GPD_GE_014 = Version(geopandas.__version__) >= Version("0.14.0")


def overlaps(gdf):
    if GPD_GE_014:
        i, j = gdf.sindex.query(gdf.geometry, predicate="overlaps").T
    else:
        i, j = gdf.sindex.query_bulk(gdf.geometry, predicate="overlaps").T

    return list(zip(i, j, strict=False))


def trim_overlaps(gdf, largest=True, inplace=False):
    """Trim overlapping polygons


    Parameters
    ----------

    gdf:  geodataframe with polygon geometries

    largest: boolean
             True: trim the larger of the pair of overlapping polygons,
             False: trim the smaller polygon.

    Returns
    -------

    gdf: geodataframe with corrected geometries

    """
    if GPD_GE_014:
        intersections = gdf.sindex.query(gdf.geometry, predicate="intersects").T
    else:
        intersections = gdf.sindex.query_bulk(gdf.geometry, predicate="intersects").T

    if not inplace:
        gdf = gdf.copy()
    if largest:
        for i, j in intersections:
            if i != j:
                left = gdf.geometry[i]
                right = gdf.geometry[j]
                if left.area < right.area:
                    right = gdf.geometry[j].difference(gdf.geometry[i])
                    gdf.loc[j, gdf.geometry.name] = right
                else:
                    left = gdf.geometry[i].difference(gdf.geometry[j])
                    gdf.loc[i, gdf.geometry.name] = left
    else:
        for i, j in intersections:
            if i != j:
                left = gdf.geometry[i]
                right = gdf.geometry[j]
                if left.area > right.area:
                    right = gdf.geometry[j].difference(gdf.geometry[i])
                    gdf.loc[j, gdf.geometry.name] = right
                else:
                    left = gdf.geometry[i].difference(gdf.geometry[j])
                    gdf.loc[i, gdf.geometry.name] = left

    return gdf


def is_overlapping(gdf):
    "Test for overlapping features in geoseries."

    if GPD_GE_014:
        overlaps = gdf.sindex.query(gdf.geometry, predicate="overlaps")
    else:
        overlaps = gdf.sindex.query_bulk(gdf.geometry, predicate="overlaps")

    if overlaps.shape[1] > 0:
        return True
    return False
