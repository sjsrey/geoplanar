geoplanar
=========

Planar enforcement for polygon geoseries

.. figure:: https://i.imgur.com/CFgnecL.png
   :alt: mexico-us

   mexico-us

|unittests| \|\ |Documentation Status| |DOI|

``geoplanar`` supports the detection and correction of violations of
`planar
enforcement <https://ibis.geog.ubc.ca/courses/klink/gis.notes/ncgia/u12.html#SEC12.6>`__
for polygon geoseries including:

-  `gaps <https://github.com/sjsrey/geoplanar/blob/main/notebooks/gaps.ipynb>`__
-  `nonplanar coincident
   edges <https://github.com/sjsrey/geoplanar/blob/main/notebooks/nonplanaredges.ipynb>`__
-  `nonplanar
   touches <https://github.com/sjsrey/geoplanar/blob/main/notebooks/nonplanartouches.ipynb>`__
-  `overlaps <https://github.com/sjsrey/geoplanar/blob/main/notebooks/overlaps.ipynb>`__
-  `holes <https://github.com/sjsrey/geoplanar/blob/main/notebooks/holes.ipynb>`__

Status
------

``geoplanar`` is currently in alpha status and is open to contributions
that help shape the scope of the package. It is being developed in
support of
`research <https://nsf.gov/awardsearch/showAward?AWD_ID=1759746&HistoricalAwards=false>`__
and is likely to be undergoing changes as the project evolves.

Contributing
------------

``geoplanar`` development uses a
`git-flow <https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow>`__
model. Contributions following this model are welcomed.

Funding
-------

``geoplanar`` is partially supported by `NSF Award #1759746, Comparative
Regional Inequality Dynamics: Multiscalar and Multinational
Perspectives <https://nsf.gov/awardsearch/showAward?AWD_ID=1759746&HistoricalAwards=false>`__

.. |unittests| image:: https://github.com/sjsrey/geoplanar/workflows/.github/workflows/unittests.yml/badge.svg
   :target: https://github.com/sjsrey/geoplanar/actions?query=workflow%3A.github%2Fworkflows%2Funittests.yml
.. |Documentation Status| image:: https://readthedocs.org/projects/geoplanar/badge/?version=latest
   :target: https://geoplanar.readthedocs.io/en/latest/?badge=latest
.. |DOI| image:: https://zenodo.org/badge/382492314.svg
   :target: https://zenodo.org/badge/latestdoi/382492314
