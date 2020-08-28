"""
Geometry factories based on the geo interface
"""
import warnings

from shapely.errors import ShapelyDeprecationWarning

from .point import Point
from .linestring import LineString
from .polygon import Polygon
from .multipoint import MultiPoint
from .multilinestring import MultiLineString
from .multipolygon import MultiPolygon
from .collection import GeometryCollection

# numpy is an optional dependency
try:
    import numpy as np
except ImportError:
    _has_numpy = False
else:
    _has_numpy = True


def _is_coordinates_empty(coordinates):
    """Helper to identify if coordinates or subset of coordinates are empty"""

    if coordinates is None:
        return True

    is_numpy_array = _has_numpy and isinstance(coordinates, np.ndarray)
    if isinstance(coordinates, (list, tuple)) or is_numpy_array:
        if len(coordinates) == 0:
            return True
        return all(map(_is_coordinates_empty, coordinates))
    else:
        return False


def _empty_shape_for_no_coordinates(geom_type):
    """Return empty counterpart for geom_type"""
    if geom_type == 'point':
        return Point()
    elif geom_type == 'multipoint':
        return MultiPoint()
    elif geom_type == 'linestring':
        return LineString()
    elif geom_type == 'multilinestring':
        return MultiLineString()
    elif geom_type == 'polygon':
        return Polygon()
    elif geom_type == 'multipolygon':
        return MultiPolygon()
    else:
        raise ValueError("Unknown geometry type: %s" % geom_type)


def box(minx, miny, maxx, maxy, ccw=True):
    """Returns a rectangular polygon with configurable normal vector"""
    coords = [(maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)]
    if not ccw:
        coords = coords[::-1]
    return Polygon(coords)


def shape(context):
    """
    Returns a new, independent geometry with coordinates *copied* from the
    context. Changes to the original context will not be reflected in the
    geometry object.

    Parameters
    ----------
    context :
        a GeoJSON-like dict, which provides a "type" member describing the type
        of the geometry and "coordinates" member providing a list of coordinates,
        or an object which implements __geo_interface__.

    Returns
    -------
    Geometry object

    Example
    -------
    Create a Point from GeoJSON, and then create a copy using __geo_interface__.

    >>> context = {'type': 'Point', 'coordinates': [0, 1]}
    >>> geom = shape(context)
    >>> geom.type == 'Point'
    True
    >>> geom.wkt
    'POINT (0 1)'
    >>> geom2 = shape(geom)
    >>> geom == geom2
    True
    """
    if hasattr(context, "__geo_interface__"):
        ob = context.__geo_interface__
    else:
        ob = context
    geom_type = ob.get("type").lower()
    if 'coordinates' in ob and _is_coordinates_empty(ob['coordinates']):
        return _empty_shape_for_no_coordinates(geom_type)
    elif geom_type == "point":
        return Point(ob["coordinates"])
    elif geom_type == "linestring":
        return LineString(ob["coordinates"])
    elif geom_type == "polygon":
        return Polygon(ob["coordinates"][0], ob["coordinates"][1:])
    elif geom_type == "multipoint":
        return MultiPoint(ob["coordinates"])
    elif geom_type == "multilinestring":
        return MultiLineString(ob["coordinates"])
    elif geom_type == "multipolygon":
        return MultiPolygon(ob["coordinates"], context_type='geojson')
    elif geom_type == "geometrycollection":
        geoms = [shape(g) for g in ob.get("geometries", [])]
        return GeometryCollection(geoms)
    else:
        raise ValueError("Unknown geometry type: %s" % geom_type)


def mapping(ob):
    """
    Returns a GeoJSON-like mapping from a Geometry or any
    object which implements __geo_interface__

    Parameters
    ----------
    ob :
        An object which implements __geo_interface__.

    Returns
    -------
    dict

    Example
    -------
    >>> pt = Point(0, 0)
    >>> mapping(p)
    {'type': 'Point', 'coordinates': (0.0, 0.0)}
    """
    return ob.__geo_interface__
