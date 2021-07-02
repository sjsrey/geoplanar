#!/usr/bin/env python3
#
import pandas
import geopandas
from shapely.geometry import box


def holes(gdf):
    """Find holes in a geodataframe"""


    # get box
    b = box(*gdf.total_bounds)

    # form unary union
    u = gdf.unary_union

    # diff of b and u
    dbu = geopandas.GeoDataFrame(geometry=[b.difference(u)])

    # explode
    _holes = dbu.explode()

    # hull
    hull = gdf.dissolve().convex_hull

    # return holes
    _holes =  _holes[_holes.within(hull.geometry[0])]

    return _holes


def fill_holes(gdf):
    h = holes(gdf)
    for index, row in h.iterrows():
        #print(row.geometry.area)
        rdf = geopandas.GeoDataFrame(geometry=[row.geometry])
        neighbors = geopandas.sjoin(left_df=gdf,
                                   right_df=rdf,
                                   how='inner',
                                   op='intersects')
        largest = neighbors[neighbors.area==neighbors.area.max()]
        tmpdf = pandas.concat([largest, rdf]).dissolve()
        gdf.geometry[largest.index] = tmpdf.geometry[0]
        #print(largest.head())
    return gdf
