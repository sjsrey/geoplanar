#!/usr/bin/env python3
import geopandas
import libpysal
import numpy as np
from collections import defaultdict
from packaging.version import Version

__all__ = ["overlaps", "trim_overlaps", "is_overlapping", "merge_overlaps", "merge_touching"]

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
  
def merge_overlaps(gdf, merge_limit, overlap_limit):
    """Merge overlapping polygons based on a set of conditions.

    Overlapping polygons smaller than ``merge_limit`` are merged to a neighboring polygon.

    Polygons larger than ``merge_limit`` are merged to neighboring if they share area larger
    than ``area * overlap_limit``.

    Parameters
    ----------
    gdf : GeoDataFrame
        GeoDataFrame with polygon or mutli polygon geometry
    merge_limit : float
        area of overlapping polygons that are to be merged with neighbors no matter the size
        of the overlap
    overlap_limit : float (0-1)
        ratio of area of an overlapping polygon that has to be shared with other polygon
        to merge both into one
    
    Returns
    -------

    GeoDataFrame
    """
    if GPD_GE_014:
        overlap_a, overlap_b = gdf.sindex.query(gdf.geometry, predicate="overlaps")
        contains_a, contains_b = gdf.sindex.query(gdf.geometry, predicate="contains")
    else:
        overlap_a, overlap_b = gdf.sindex.query_bulk(gdf.geometry, predicate="overlaps")
        contains_a, contains_b = gdf.sindex.query_bulk(gdf.geometry, predicate="contains")

    self_mask = contains_a != contains_b
    contains_a = contains_a[self_mask]
    contains_b = contains_b[self_mask]

    self_mask = overlap_a != overlap_b
    overlap_a = overlap_a[self_mask]
    overlap_b = overlap_b[self_mask]

    source = np.concatenate([overlap_a, contains_a])
    target = np.concatenate([overlap_b, contains_b])

    neighbors = defaultdict(list)
    for key, value in zip(source, target):
        neighbors[key].append(value)

    neighbors_final = {}

    for i, poly in gdf.geometry.items():
        if i in neighbors:
            if poly.area < merge_limit:
                neighbors_final[i] = neighbors[i]
            else:
                sub = gdf.geometry.iloc[neighbors[i]]
                inters = sub.intersection(poly)
                include = sub.index[inters.area > (sub.area * overlap_limit)]
                neighbors_final[i] = list(include)
        else:
            neighbors_final[i]=[]

    W = libpysal.weights.W(neighbors_final, silence_warnings=True)
    return gdf.dissolve(W.component_labels)

def merge_touching(gdf, index, largest=None):
    """Merge or remove polygons based on a set of conditions.
    If polygon does not share any boundary with another polygon, remove. If it shares some boundary with
    a neighbouring polygon, join to that polygon. If ``largest=None`` it picks one randomly, otherwise it 
    picks the polygon with which it shares the largest (True) or the smallest (False) boundary.

    Parameters
    ----------
    gdf : GeoDataFrame
        GeoDataFrame with polygon or mutli polygon geometry
    index : list of indexes
        list of indexes of polygons in gdf to merge or remove
    largest : bool (default None)
        Merge with the polygon with the largest (True) or smallest (False) shared boundary.
        If None, merge with any neighbor non-deterministically but performantly.

    Returns
    -------

    GeoDataFrame
    """
    
    merge_gdf = gdf.loc[index]

    if GPD_GE_014:
        source, target = gdf.boundary.sindex.query(merge_gdf.boundary, predicate="overlaps")
    else:
        source, target = gdf.boundary.sindex.query_bulk(merge_gdf.boundary, predicate="overlaps")

    source = merge_gdf.index[source]
    target = gdf.index[target]

    neighbors={}
    delete = []
    for i, poly in gdf.geometry.items():
        if i in merge_gdf.index:
            if i in source:
                if largest is None:
                    neighbors[i]=[target[source==i][0]]
                else:
                    sub = gdf.geometry.loc[target[source==i]]
                    inters = sub.intersection(poly.exterior)
                    if largest:
                        neighbors[i] = [inters.length.idxmax()]
                    else:
                        neighbors[i] = [inters.length.idxmin()]
            else:
                delete.append(i)
        else:
            neighbors[i]=[]

    W = libpysal.weights.W(neighbors, silence_warnings=True)
    return gdf.drop(delete).dissolve(W.component_labels)

