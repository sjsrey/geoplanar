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
import geoplanar
import geopandas

```

```python
states = geopandas.read_file("../geoplanar/datasets/india/Admin2.shp")
states.plot()
```

```python
geoplanar.is_planar_enforced(states)
```

```python
geoplanar.self_intersecting_rings(states)
```

```python
geoplanar.check_validity(states)
```

```python

```
