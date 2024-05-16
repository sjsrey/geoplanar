#!/usr/bin/env python3
#
import pandas as pd
import numpy as np
import geopandas
import shapely
from packaging.version import Version

__all__ = ["gaps", "fill_gaps", "snap"]

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

def _snap(geometry, reference, threshold, segment_length):
    """Snap g1 to g2 within threshold

    Parameters
    ----------
    geometry : shapely.Polygon
        geometry to snap
    reference : shapely.Polygon
        geometry to snap to
    threshold : float
        max distance between vertices to snap
    segment_length : float
        max segment length parameter in segmentize

    Returns
    -------
    shapely.Polygon
        snapped geometry
    """

    # extract the shell and holes from the first geometry
    shell, holes = geometry.exterior, geometry.interiors
    # segmentize the shell and extract coordinates
    coords = shapely.get_coordinates(shapely.segmentize(shell, segment_length))
    # create a point geometry from the coordinates
    points = shapely.points(coords)
    # find the shortest line between the points and the second geometry
    lines = shapely.shortest_line(points, reference)
    # mask the coordinates where the distance is less than the threshold
    distance_mask = shapely.length(lines) < threshold

    # return the original geometry if no coordinates are within the threshold
    if not any(distance_mask):
        return geometry

    # update the coordinates with the snapped coordinates
    coords[distance_mask] = shapely.get_coordinates(lines)[1::2][distance_mask]
    # re-create the polygon with new coordinates and original holes and simplify
    # to remove any extra vertices
    return shapely.simplify(shapely.Polygon(coords, holes=holes), segment_length / 100)

def snap(geometry, threshold=0.5):
    """Snap geometries that are within threshold to each other

    Only one of the pair of geometries identified as nearby will be snapped,
    the one with the lower index.

    Parameters
    ----------
    geometry : GeoDataFrame | GeoSeries
        geometries to snap. Geometry type needs to be Polygon for all of them.
    threshold : float, optional
        max distance between geometries to snap, by default 0.5
        threshold should be ~10% larger than the distance between polygon edges to ensure snapping

    Returns
    -------
    GeoSeries
        GeoSeries with snapped geometries
    """
    
    nearby_a, nearby_b = geometry.sindex.query(
        geometry.geometry, predicate="dwithin", distance=threshold
    )
    overlap_a, overlap_b = geometry.boundary.sindex.query(
        geometry.boundary, predicate="overlaps"
    )

    self_mask = nearby_a != nearby_b
    nearby_a = nearby_a[self_mask]
    nearby_b = nearby_b[self_mask]

    self_mask = overlap_a != overlap_b
    overlap_a = overlap_a[self_mask]
    overlap_b = overlap_b[self_mask]

    nearby = pd.MultiIndex.from_arrays([nearby_a, nearby_b], names=("source", "target"))
    overlap = pd.MultiIndex.from_arrays(
        [overlap_a, overlap_b], names=("source", "target")
    )
    nearby_not_overlap = nearby.difference(overlap)
    if nearby_not_overlap.empty == False:
        duplicated = pd.DataFrame(
            np.sort(np.array(nearby_not_overlap.to_list()), axis=1)
        ).duplicated()
        pairs_to_snap = nearby_not_overlap[~duplicated]
    
        new_geoms = []
        previous_geom=0
        snapped_geom=0
        for geom, ref in zip(
            geometry.geometry.iloc[pairs_to_snap.get_level_values("source")],
            geometry.geometry.iloc[pairs_to_snap.get_level_values("target")],
        ):

            if previous_geom == geom:
                new_geoms.append(
                    _snap(snapped_geom, ref, threshold=threshold, segment_length=threshold)
                )
            else:
                snapped_geom = _snap(geom, ref, threshold=threshold, segment_length=threshold)
                new_geoms.append(snapped_geom)
                previous_geom = geom

        snapped = geometry.geometry.copy()
        snapped.iloc[pairs_to_snap.get_level_values("source")] = new_geoms
    else:
        snapped = geometry.geometry.copy()
    return snapped
