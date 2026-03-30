import geopandas as gpd
from shapely.geometry import Point

gdf = gpd.read_file("data/ghana_regions.geojson")

sindex = gdf.sindex


def _region_from_coords(lat: float, lon: float) -> str:
    point = Point(lon, lat)

    possible_idx = list(sindex.intersection(point.bounds))

    for idx in possible_idx:
        row = gdf.iloc[idx]
        if row.geometry.contains(point):
            return row["shapeName"]

    return "Unknown"

