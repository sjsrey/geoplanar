#!/usr/bin/env python3

from shapely import validity

def isvalid(obj):
    return validity.explain_validity(obj)
