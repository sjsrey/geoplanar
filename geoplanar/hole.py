#!/usr/bin/env python3
#
import pandas
import geopandas
from shapely.geometry import box
import shapely


def holes(gdf):
    """Find holes in a geodataframe.

    A hole is also known as a sliver which contains a set of points that:

    - are not contained by any of the geometries in the geoseries
    - are contained in the convex hull of the unary_union of the geoseries

    Parameters
    ----------

    gdf :  GeoDataFrame with polygon (multipolygon) GeoSeries


    Returns
    -------

    _holes : GeoDataFrame with hole polygons

    Examples
    --------
    >>> p1 = box(0,0,10,10)
    >>> p2 = Polygon([(10,10), (12,8), (10,6), (12,4), (10,2), (20,5)])
    >>> gdf = geopandas.GeoDataFrame(geometry=[p1,p2])
    >>> h = geoplanar.holes(gdf)
    >>> h.area
    array([4., 4.])
    """

    # get box
    b = box(*gdf.total_bounds)

    # form unary union
    u = gdf.unary_union

    # diff of b and u
    dbu = geopandas.GeoDataFrame(geometry=[b.difference(u)])

    # explode
    _holes = dbu.explode()


    _holes.reset_index(inplace=True)

    gaps = []
    for idx, row in _holes.iterrows():
        its = b.exterior.intersection(row.geometry)
        if not isinstance(its, shapely.geometry.multilinestring.MultiLineString):
            gaps.append(idx)

    return _holes.iloc[gaps]



def fill_holes(gdf, largest=True, inplace=False):
    """Fill any holes in a geodataframe.

    A hole is also known as a sliver which contains a set of points that:

    - are not contained by any of the geometries in the geoseries
    - are contained in the convex hull of the unary_union of the geoseries

    Parameters
    ----------

    gdf :  GeoDataFrame with polygon (multipolygon) GeoSeries


    largest: boolean (Default: True)
          Merge each hole with its largest (True), or smallest (False) touching neighbor

    inplace: boolean (default: False)
          Change the geoseries of current dataframe


    Returns
    -------

    _holes : GeoDataFrame with hole polygons

    Examples
    --------
    >>> p1 = box(0,0,10,10)
    >>> p2 = Polygon([(10,10), (12,8), (10,6), (12,4), (10,2), (20,5)])
    >>> gdf = geopandas.GeoDataFrame(geometry=[p1,p2])
    >>> gdf.area
    0    100.0
    1     32.0
    dtype: float64
    >>> h = geoplanar.holes(gdf)
    >>> h.area
    array([4., 4.])
    >>> gdf1 = geoplanar.fill_holes(gdf)
    >>> gdf1.area
    0    108.0
    1     32.0
    dtype: float64
    """


    h = holes(gdf)
    if not inplace:
        gdf = gdf.copy()

    for index, row in h.iterrows():
        rdf = geopandas.GeoDataFrame(geometry=[row.geometry])
        neighbors = geopandas.sjoin(left_df=gdf, right_df=rdf, how='inner',
                                    op='intersects')
        if largest:
            left = neighbors[neighbors.area==neighbors.area.max()]
        else:
            left = neighbors[neighbors.area==neighbors.area.min()]
        tmpdf = pandas.concat([left, rdf]).dissolve()
        try:
            geom = tmpdf.loc[0, 'geometry']
            gdf.geometry[left.index] = geopandas.GeoDataFrame(geometry=[geom]).geometry.values
        except:
            print(index, tmpdf.shape)

    return gdf

def missing_interiors(gdf):
    """ Find any missing interiors.

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
    contained = gdf.geometry.sindex.query_bulk(gdf.geometry,
                                               predicate="contains")
    pairs = []
    for pair in contained.T:
        i,j = pair
        if i != j:
            pairs.append((i,j))
    return pairs


def add_interiors(gdf, inplace=False):
    """ Add any missing interiors.

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

    contained = gdf.geometry.sindex.query_bulk(gdf.geometry,
                                               predicate="contains")
    a, k = contained.shape
    n = gdf.shape[0]
    if k > gdf.shape[0]:
        to_add = contained[:, contained[0] != contained[1]].T
        for add in to_add:
            i, j = add
            gdf.geometry[i] = gdf.geometry[i].difference(gdf.geometry[j])
    return gdf
