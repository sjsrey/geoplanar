#!/usr/bin/env python3
import numpy
import geopandas

from packaging.version import Version

GPD_GE_014 = Version(geopandas.__version__) >= Version("0.14.0")


def overlaps(gdf):
    pairs = []
    if GPD_GE_014:
        intersections = gdf.sindex.query(gdf.geometry, predicate="intersects").T
    else:
        intersections = gdf.sindex.query_bulk(gdf.geometry, predicate="intersects").T

    for i, j in intersections:
        if i != j:
            pairs.append((i, j))

    return pairs


def trim_overlaps(gdf, largest=True, inplace=False):
    """Trim overlapping polygons


    Parameters
    ----------

    gdf:  geodataframe with polygon geometries

    largest: boolean
             True: trim the larger of the pair of overlapping polygons, False: trim the smaller polygon.

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

    uu = gdf.unary_union
    area_sum = gdf.area.sum()
    if not numpy.isclose(area_sum, uu.area):
        return True
    return False
