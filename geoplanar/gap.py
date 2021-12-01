#!/usr/bin/env python3
#
import pandas
import geopandas
from shapely.geometry import box
import shapely


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

    # get box
    b = box(*gdf.total_bounds)

    # form unary union
    u = gdf.unary_union

    # diff of b and u
    dbu = geopandas.GeoDataFrame(geometry=[b.difference(u)])

    # explode
    _gaps = dbu.explode(index_parts=False, ignore_index=True)

    # gaps are polygons that do not share an edge with the bounding box of the union
    gaps = []
    for idx, row in _gaps.iterrows():
        its = b.exterior.intersection(row.geometry)
        if not isinstance(its, shapely.geometry.multilinestring.MultiLineString):
            gaps.append(idx)

    return _gaps.iloc[gaps]



def fill_gaps(gdf, gap_df=None, largest=True, inplace=False):
    """Fill any gaps in a geodataframe.

    Parameters
    ----------

    gdf :  GeoDataFrame with polygon (multipolygon) GeoSeries
    

    gap_df:  GeoDataFrame with gaps to fill
             If None, gaps will be determined
    
    largest: boolean (Default: True)
          Merge each gap with its largest (True), or smallest (False) neighbor

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


    if gap_df is None:
        gap_df = gaps(gdf)

    if not inplace:
        gdf = gdf.copy()

    for index, row in gap_df.iterrows():
        rdf = geopandas.GeoDataFrame(geometry=[row.geometry])
        neighbors = geopandas.sjoin(left_df=gdf, right_df=rdf, how='inner',
                                    predicate='intersects')
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
