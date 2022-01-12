---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.11.3
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
import geopandas
import numpy
import matplotlib.pyplot as plt
import geoplanar
from shapely.geometry import box, Point

```

# Omitted interiors


For a planar enforced polygon layer there should be no individual polygons that are contained inside other polygons.

Violation of this condition can lead to a number of errors in subsequent spatial analysis.

## Violation: Points within more than a single feature


If this were not the case, then it would be possible for a point to be contained inside more than a single polygon which would be a violation of planar enforcement.
An example can be seen as follows:

```python
p1 = box(0,0,10,10)
p2 = box(1,1, 3,3)
p3 = box(7,7, 9,9)

gdf = geopandas.GeoDataFrame(geometry=[p1,p2,p3])
base = gdf.plot(edgecolor='k')

pnt1 = geopandas.GeoDataFrame(geometry=[Point(2,2)])
pnt1.plot(ax=base,color='red')
```

```python
pnt1.within(gdf.geometry[0])
```

```python
pnt1.within(gdf.geometry[1])
```
The violation here is that `pnt1` is `within` *both* polygon `p1` *and* `p2`.


## Error in area calculations

A related error that arises in this case is that the area of the "containing" polygon will be too large, since it includes the area of the smaller polygons:

```python
gdf.geometry[0]
```

```python
gdf.area
```

```python
gdf.area.sum()
```

## Missing interior rings (aka holes)

The crux of the issue is that the two smaller polygons are entities in their own right, yet the large polygon was defined to have only a single external ring. It is missing two **interior rings**
which would allow for the correct topological relationship between the larger polygon and the two smaller polygons.

`geoplanar` can detect missing interiors:

```python
mi = geoplanar.missing_interiors(gdf)
mi
```


## Adding interior rings
Once we know that the problem is missing interior rings, we can correct this with `add_interiors`:

```python
gdf1 = geoplanar.add_interiors(gdf)
```

```python
gdf1.geometry[0]
```

And we see that the resulting area of the GeoSeries is now correct:

```python
gdf1.area
```
Additionally, a check for `missing_interiors` reveals the violation has been corrected

```python
geoplanar.missing_interiors(gdf1)
```

The addition of the interior rings also corrects the violation of the containment rule that a point should belong to at most a single polygon in a planar enforced polygon GeoSeries:


```python
pnt1.within(gdf1.geometry[0])
```

```python
pnt1.within(gdf1.geometry[1])
```
## Failure to detect contiguity

A final implication of missing interiors in a non-planar enforced polygon GeoSeries is that algorithms that rely on planar enforcement to detect contiguous polygons will fail.

More specifically, in [pysal](https://pysal.org), fast polygon detectors can be used to generate so called Queen neighbors, which are pairs of polygons that share at least one vertex on their exterior/interior rings.

```python
import libpysal
```


```python
w = libpysal.weights.Queen.from_dataframe(gdf)
```

```python
w.neighbors
```
The original GeoDataFrame results in fully disconnected polygons, or islands. `pysal` at least throws a warning when islands are detected, and for this particular type of planar enforcement violation, missing interiors, the contained polygons will always be reported as islands.

Using the corrected GeoDataFrame with the inserted interior rings results in the correct neighbor determinations:
```python
w = libpysal.weights.Queen.from_dataframe(gdf1)
```

```python
w.neighbors
```
