#!/usr/bin/env python3
#
import pandas
import geopandas
from shapely.geometry import box
import shapely

from packaging.version import Version

GPD_GE_014 = Version(geopandas.__version__) >= Version("0.14.0")


def missing_interiors(gdf):
    """Find any missing interiors.

    For a planar enforced polygon layer, there should be no cases of a polygon
    being contained in another polygon. Instead the "contained" polygon is a
    hole in the "containing" polygon.


    Parameters
    ----------

    gdf :  GeoDataFrame with polygon (multipolygon) GeoSeries


    Returns
    -------

    pairs : list
           tuples for each violation (i,j), where i is the index of the
           containing polygon, j is the index of the contained polygon

    Examples
    --------
    >>> p1 = box(0,0,10,10)
    >>> p2 = box(1,1, 3,3)
    >>> p3 = box(7,7, 9,9)
    >>> gdf = geopandas.GeoDataFrame(geometry=[p1,p2,p3])
    >>> mi = geoplanar.missing_interiors(gdf)
    >>> mi
    [(0, 1), (0, 2)]
    """
    if GPD_GE_014:
        contained = gdf.geometry.sindex.query(gdf.geometry, predicate="contains")
    else:
        contained = gdf.geometry.sindex.query_bulk(gdf.geometry, predicate="contains")
    pairs = []
    for pair in contained.T:
        i, j = pair
        if i != j:
            pairs.append((i, j))
    return pairs


def add_interiors(gdf, inplace=False):
    """Add any missing interiors.

    For a planar enforced polygon layer, there should be no cases of a polygon
    being contained in another polygon. Instead the "contained" polygon is a
    hole in the "containing" polygon. This function finds and corrects any such violations.


    Parameters
    ----------

    gdf :  GeoDataFrame with polygon (multipolygon) GeoSeries


    inplace: boolean (default: False)
          Change the geoseries of current dataframe


    Returns
    -------

    gdf : GeoDataFrame


    Examples
    --------
    >>> p1 = box(0,0,10,10)
    >>> p2 = box(1,1, 3,3)
    >>> p3 = box(7,7, 9,9)
    >>> gdf = geopandas.GeoDataFrame(geometry=[p1,p2,p3])
    >>> gdf.area
    0   100.0
    1     4.0
    2     4.0
    >>> mi = geoplanar.missing_interiors(gdf)
    >>> mi
    [(0, 1), (0, 2)]
    >>> gdf1 = geoplanar.add_interiors(gdf)
    >>> gdf1.area
    0    92.0
    1     4.0
    2     4.0
    """
    if not inplace:
        gdf = gdf.copy()

    if GPD_GE_014:
        contained = gdf.geometry.sindex.query(gdf.geometry, predicate="contains")
    else:
        contained = gdf.geometry.sindex.query_bulk(gdf.geometry, predicate="contains")
    a, k = contained.shape
    n = gdf.shape[0]
    if k > gdf.shape[0]:
        to_add = contained[:, contained[0] != contained[1]].T
        for add in to_add:
            i, j = add
            gdf.loc[i, gdf.geometry.name] = gdf.geometry[i].difference(gdf.geometry[j])
    return gdf
