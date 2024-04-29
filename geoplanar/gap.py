#!/usr/bin/env python3
#
import geopandas
import shapely
from packaging.version import Version

__all__ = ["gaps", "fill_gaps"]

GPD_GE_014 = Version(geopandas.__version__) >= Version("0.14.0")
GPD_GE_100 = Version(geopandas.__version__) >= Version("1.0.0dev")


def gaps(gdf):
    """Find gaps in a geodataframe.

    A gap (emply sliver polygon) is a set of points that:

    - are not contained by any of the geometries in the geoseries
    - are not contained by the external polygon

    Parameters
    ----------

    gdf :  GeoDataFrame with polygon (multipolygon) GeoSeries


    Returns
    -------

    _gaps : GeoDataFrame with gap polygons

    Examples
    --------
    >>> p1 = box(0,0,10,10)
    >>> p2 = Polygon([(10,10), (12,8), (10,6), (12,4), (10,2), (20,5)])
    >>> gdf = geopandas.GeoDataFrame(geometry=[p1,p2])
    >>> h = geoplanar.gaps(gdf)
    >>> h.area
    array([4., 4.])
    """

    polygons = geopandas.GeoSeries(
        shapely.get_parts(
            shapely.polygonize(
                [gdf.boundary.union_all() if GPD_GE_100 else gdf.boundary.unary_union]
            )
        ),
        crs=gdf.crs,
    )
    if GPD_GE_014:
        poly_idx, _ = gdf.sindex.query(polygons, predicate="covers")
    else:
        poly_idx, _ = gdf.sindex.query_bulk(polygons, predicate="covers")

    return polygons.drop(poly_idx).reset_index(drop=True)


def fill_gaps(gdf, gap_df=None, largest=True, inplace=False):
    """Fill any gaps in a geodataframe.

    Parameters
    ----------

    gdf :  GeoDataFrame with polygon (multipolygon) GeoSeries


    gap_df:  GeoDataFrame with gaps to fill
             If None, gaps will be determined

    largest: boolean (Default: True)
          Merge each gap with its largest (True), or smallest (False) neighbor.
          If None, merge with any neighbor non-deterministically but performantly.

    inplace: boolean (default: False)
          Change the geoseries of current dataframe


    Returns
    -------

    _gaps : GeoDataFrame with gap polygons

    Examples
    --------
    >>> p1 = box(0,0,10,10)
    >>> p2 = Polygon([(10,10), (12,8), (10,6), (12,4), (10,2), (20,5)])
    >>> gdf = geopandas.GeoDataFrame(geometry=[p1,p2])
    >>> gdf.area
    0    100.0
    1     32.0
    dtype: float64
    >>> h = geoplanar.gaps(gdf)
    >>> h.area
    array([4., 4.])
    >>> gdf1 = geoplanar.fill_gaps(gdf)
    >>> gdf1.area
    0    108.0
    1     32.0
    dtype: float64
    """
    from collections import defaultdict

    if gap_df is None:
        gap_df = gaps(gdf)

    if not inplace:
        gdf = gdf.copy()

    if not GPD_GE_014:
        gap_idx, gdf_idx = gdf.sindex.query_bulk(
            gap_df.geometry, predicate="intersects"
        )
    else:
        gap_idx, gdf_idx = gdf.sindex.query(gap_df.geometry, predicate="intersects")

    to_merge = defaultdict(set)
    for g_ix in range(len(gap_df)):
        neighbors = gdf_idx[gap_idx == g_ix]
        if largest is None:  # don't care which polygon is a gap attached to
            to_merge[neighbors[0]].add(g_ix)
        elif largest:
            to_merge[gdf.iloc[neighbors].area.idxmax()].add(g_ix)
        else:
            to_merge[gdf.iloc[neighbors].area.idxmin()].add(g_ix)

    new_geom = []
    for k, v in to_merge.items():
        new_geom.append(
            shapely.union_all(
                [gdf.geometry.iloc[k]] + [gap_df.geometry.iloc[i] for i in v]
            )
        )
    gdf.loc[gdf.index.take(list(to_merge.keys())), gdf.geometry.name] = new_geom

    return gdf
