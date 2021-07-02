#!/usr/bin/env python3

from shapely import validation

def isvalid(obj):
    return validation.explain_validity(obj)
