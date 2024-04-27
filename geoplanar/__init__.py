"""
GeoPlanar

A module for handling planar enforcement for polygon geoseries.
"""

import contextlib
from importlib.metadata import PackageNotFoundError, version

from geoplanar.gap import *
from geoplanar.hole import *
from geoplanar.overlap import *
from geoplanar.planar import *
from geoplanar.valid import *

with contextlib.suppress(PackageNotFoundError):
    __version__ = version("geoplanar")
