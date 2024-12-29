import pytest
from shapely.geometry import box
import geopandas as gpd
from geoplanar import fill_gaps  # Updated module name
from packaging.version import Version
import pytest

@pytest.mark.skipif(Version(gpd.__version__) == Version("0.10.2"), reason="Missing pygeos")    
def test_fill_gaps_compact_visual_case():
    """Test fill_gaps behavior with compact=True and compact=False using specific geometries."""
    # Define four polygons with a visible gap
    p1 = box(0, 0, 10, 10)     # Left rectangle
    p2 = box(10, 0, 40, 2)     # Bottom thin rectangle
    p3 = box(10, 3, 40, 10)    # Top thin rectangle
    p4 = box(40, 0, 100, 10)   # Right rectangle

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(geometry=[p1, p2, p3, p4])

    # Fill gaps with compact
    filled_gdf_compact = fill_gaps(gdf, strategy='compact')
    compact_geom_count = len(filled_gdf_compact)

    # Fill gaps with largest (default)
    filled_gdf_default = fill_gaps(gdf, strategy='largest')
    default_geom_count = len(filled_gdf_default)

    # Assert the number of geometries is the same after filling gaps
    assert compact_geom_count == default_geom_count, (
        "The number of geometries after filling gaps should remain consistent."
    )

    # Assert the geometries differ when compact=True vs largest=True
    assert not filled_gdf_compact.equals(filled_gdf_default), (
        "The resulting geometries should differ between compact=True and largest=True."
    )

    # Verify that gaps are filled completely
    filled_gaps_compact = filled_gdf_compact.unary_union
    filled_gaps_default = filled_gdf_default.unary_union
    assert filled_gaps_compact.is_valid, "The geometries with compact=True must be valid."
    assert filled_gaps_default.is_valid, "The geometries with largest=True must be valid."

