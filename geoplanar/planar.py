#!/usr/bin/env python3
import libpysal
import geopandas
from collections import defaultdict
from shapely.geometry import box, LineString, Polygon, Point, MultiPolygon
from shapely.ops import split, linemerge, polygonize
from .overlap import is_overlapping, overlaps
from .hole import missing_interiors
from .gap import gaps


def non_planar_edges(gdf):
    """Find coincident nonplanar edges


    Parameters
    ----------

    gdf :  GeoDataFrame with polygon (multipolygon) GeoSeries


    Returns
    -------

    missing : dictionary
              key is origin feature, value is neighboring feature for each pair
              of coincident nonplanar edges

    Examples
    --------
    >>> c1 = [[0,0], [0, 10], [10, 10], [10, 0], [0, 0]]
    >>> p1 = Polygon(c1)
    >>> c2 = [[10, 2], [10, 8], [20, 8], [20, 2], [10, 2]]
    >>> p2 = Polygon(c2)
    >>> gdf = geopandas.GeoDataFrame(geometry=[p1, p2])
    >>> geoplanar.non_planar_edges(gdf)
    defaultdict(set, {0: {1}})

    """
    w = libpysal.weights.Queen.from_dataframe(gdf)
    intersections = gdf.sindex.query_bulk(gdf.geometry, predicate='intersects').T
    w1 = defaultdict(list)
    for i,j in intersections:
        if i != j:
            w1[i].append(j)
    missing = defaultdict(set)
    for key in w.neighbors:
        if set(w.neighbors[key]) != set(w1[key]):
            for value in w1[key]:
                pair = [key, value]
                pair.sort()
                l, r = pair
                missing[l] = missing[l].union([r])
    return missing

def planar_enforce(gdf):
    uu = gdf.unary_union
    geoms = [uu.intersection(row.geometry) for index, row in gdf.iterrows()]
    return geopandas.GeoDataFrame(geometry=geoms)

def is_planar_enforced(gdf):
    """Test if a geodataframe has any planar enforcement violations


    Parameters
    ----------


    Returns
    -------
    boolean
    """

    if is_overlapping(gdf):
        return False
    if non_planar_edges(gdf):
        return False
    _gaps = gaps(gdf)
    if _gaps.shape[0] > 0:
        return False
    return True

def fix_npe_edges(gdf, inplace=False):
    """Fix all npe intersecting edges in geoseries.

    Arguments
    ---------

    gdf: GeoDataFrame with polygon geoseries for geometry


    Returns
    -------
    gdf: GeoDataFrame with geometries respected planar edges.

    Examples
    --------
    >>> c1 = [[0,0], [0, 10], [10, 10], [10, 0], [0, 0]]
    >>> p1 = Polygon(c1)
    >>> c2 = [[10, 2], [10, 8], [20, 8], [20, 2], [10, 2]]
    >>> p2 = Polygon(c2)
    >>> gdf = geopandas.GeoDataFrame(geometry=[p1, p2])
    >>> geoplanar.non_planar_edges(gdf)
    defaultdict(set, {0: {1}})

    >>> gdf1 = geoplanar.fix_npe_edges(gdf)
    >>> geoplanar.non_planar_edges(gdf1)
    defaultdict(set, {})


    """

    if not inplace:
        gdf = gdf.copy()

    edges = non_planar_edges(gdf)
    for key in edges:
        poly_a = gdf.iloc[key].geometry
        for j in edges[key]:
            poly_b = gdf.iloc[j].geometry
            new_a, new_b = insert_intersections(poly_a, poly_b)
            poly_a = new_a
            gdf.geometry[key] = new_a
            gdf.geometry[j] = new_b
    return gdf


def insert_intersections(poly_a, poly_b):
    """Correct two npe intersecting polygons by inserting intersection points
     on intersecting edges
    """

    pint = poly_a.intersection(poly_b)
    if isinstance(pint, LineString):
        pnts = pint
        sp = [Point(pnt) for pnt in list(zip(*pnts.coords.xy))]
        new_polys = []
        for poly in [poly_a, poly_b]:
            if isinstance(poly, MultiPolygon):
                new_parts = []
                for part in poly.geoms:
                    exterior = LineString(list(part.exterior.coords))
                    for pnt in sp:
                        splits = split(exterior, pnt)
                        if len(splits.geoms) > 1:
                            left, right = splits.geoms
                            exterior = linemerge([left, right])
                    new_parts.append(Polygon(list(zip(*exterior.coords.xy))))
                new_polys.append(MultiPolygon(new_parts))                   
            else:
                exterior = LineString(list(poly.exterior.coords))
                sp = [Point(pnt) for pnt in list(zip(*pnts.coords.xy))]
                for pnt in sp:
                    splits = split(exterior, pnt)
                    if len(splits.geoms) > 1:
                        left, right = splits.geoms
                        exterior = linemerge([left, right])
                new_polys.append(Polygon(list(zip(*exterior.coords.xy))))
        return new_polys
    else:
        lin_a = LineString(list(poly_a.exterior.coords))
        lin_b = LineString(list(poly_b.exterior.coords))
        new_polys = []
        pts = lin_a.intersection(lin_b)
        for lin in [lin_a, lin_b]:
            splits = split(lin, pts).geoms
            coords = [list(zip(*line.coords.xy)) for line in list(splits)]
            new_poly = coords[0]
            for coord in coords[1:]:
                if coord[0] == new_poly[-1]:
                    new_poly.extend(coord[1:])
                else:
                    new_poly.extend(coord)
            new_polys.append(Polygon(new_poly))
        return new_polys

def self_intersecting_rings(gdf):
    sirs = []
    for i, geom in enumerate(gdf.geometry):
        if not geom.is_valid:
            sirs.append(i)
    return sirs



def fix_self_intersecting_ring(polygon):
    p0 = polygon.exterior
    mls = p0.intersection(p0)
    polys = polygonize(mls)
    return MultiPolygon(polys)


def check_validity(gdf):
    gdfv = gdf.copy()
    sirs = self_intersecting_rings(gdf)
    if sirs:
        for i in self_intersecting_rings(gdf):
            gdfv.geometry.iloc[i]= fix_self_intersecting_ring(gdfv.geometry.iloc[i])

    _gaps = gaps(gdfv)
    _overlaps = overlaps(gdfv)
    violations = {}
    violations['selfintersectingrings'] = sirs
    violations['gaps'] = _gaps
    violations['overlaps'] = _overlaps
    violations['nonplanaredges'] = non_planar_edges(gdfv)
    violations['missinginteriors'] = missing_interiors(gdfv)
    return violations
