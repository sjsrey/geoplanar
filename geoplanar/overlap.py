#!/usr/bin/env python3
import numpy


def overlaps(gdf):

    pairs = []
    intersections = gdf.sindex.query_bulk(gdf.geometry, predicate='intersects').T

    for i,j in intersections:
        if i != j:
            pairs.append((i,j))

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
    intersections = gdf.sindex.query_bulk(gdf.geometry, predicate='intersects').T

    if not inplace:
        gdf = gdf.copy()
    if largest:
        for i,j in intersections:
            if i != j:
                left = gdf.geometry[i]
                right = gdf.geometry[j]
                if left.area < right.area:
                    right = gdf.geometry[j].difference(gdf.geometry[i])
                    gdf.geometry[j] = right
                else:
                    left = gdf.geometry[i].difference(gdf.geometry[j])
                    gdf.geometry[i] = left
    else:
        for i,j in intersections:
            if i != j:
                left = gdf.geometry[i]
                right = gdf.geometry[j]
                if left.area > right.area:
                    right = gdf.geometry[j].difference(gdf.geometry[i])
                    gdf.geometry[j] = right
                else:
                    left = gdf.geometry[i].difference(gdf.geometry[j])
                    gdf.geometry[i] = left

    return gdf

def is_overlapping(gdf):
    "Test for overlapping features in geoseries."

    uu = gdf.unary_union
    area_sum = gdf.area.sum()
    if not numpy.isclose(area_sum, uu.area):
        return True
    return False
