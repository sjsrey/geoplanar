#!/usr/bin/env python3

from shapely import validation

__all__ = ["isvalid"]


def isvalid(obj):
    return validation.explain_validity(obj)
