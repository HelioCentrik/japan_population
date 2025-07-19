# scripts/prefectures_to_parquet.py
import geopandas as gpd



gdf = gpd.read_file('../data/japan_prefectures.geojson')
gdf = gdf.rename(columns={"nam": "prefecture_name", "nam_ja": "prefecture_name_ja"})
gdf["prefecture_code"] = gdf["id"].apply(lambda x: str(x * 1000).zfill(5))
gdf = gdf.sort_values(by="id").reset_index(drop=True)
gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.001, preserve_topology=True)

print(f"\n{gdf.columns}\n"
      f"{len(gdf.values)} records.\n"
      f"{gdf.values}")

# Save to Parquet
gdf.to_parquet("../data/japan_prefectures_simplified.parquet", index=False)
