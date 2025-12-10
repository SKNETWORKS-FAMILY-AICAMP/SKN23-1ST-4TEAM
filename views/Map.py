import geopandas as gpd

# 광역시도별 지도 차트
gdf = gpd.read_file("../assets/ctprvn.shp", encoding="euc-kr")
gdf = gdf.set_crs(epsg=5179)


gdf_wgs84 = gdf.to_crs(epsg=4326)
gdf_wgs84.to_file("../assets/charts/korea_sido_wgs84.geojson", driver="GeoJSON", encoding="utf-8")

print(gdf_wgs84[["CTP_KOR_NM"]])
