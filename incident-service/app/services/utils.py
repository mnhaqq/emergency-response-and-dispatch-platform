import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
GEOJSON_PATH = BASE_DIR / "data" / "ghana_regions.geojson"

gdf = gpd.read_file(GEOJSON_PATH, engine="pyogrio")

sindex = gdf.sindex


def _region_from_coords(lat: float, lon: float) -> str:
    point = Point(lon, lat)

    possible_idx = list(sindex.intersection(point.bounds))

    for idx in possible_idx:
        row = gdf.iloc[idx]
        if row.geometry.contains(point):
            return row["shapeName"]

    return "Unknown"

