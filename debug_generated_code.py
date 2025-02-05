import networkx as nx

G = nx.DiGraph()

# Input Data Nodes
G.add_node("nc_tract_shp_url", node_type="data", data_path="https://github.com/gladcolor/LLM-Geo/raw/master/overlay_analysis/tract_37_EPSG4326.zip", description="North Carolina tract boundary shapefile URL")
G.add_node("nc_hazwaste_shp_url", node_type="data", data_path="https://github.com/gladcolor/LLM-Geo/raw/master/overlay_analysis/HW_Sites_EPSG4326.zip", description="North Carolina hazardous waste sites shapefile URL")
G.add_node("nc_tract_pop_csv_url", node_type="data", data_path="https://github.com/gladcolor/LLM-Geo/raw/master/overlay_analysis/NC_tract_population.csv", description="North Carolina tract population CSV file URL")


# Operation Nodes and Data Nodes
G.add_node("load_tract_shp", node_type="operation", description="Load North Carolina tract shapefile")
G.add_edge("nc_tract_shp_url", "load_tract_shp")
G.add_node("tract_gdf", node_type="data", data_path="", description="GeoDataFrame of North Carolina tracts")
G.add_edge("load_tract_shp", "tract_gdf")

G.add_node("load_hazwaste_shp", node_type="operation", description="Load North Carolina hazardous waste sites shapefile")
G.add_edge("nc_hazwaste_shp_url", "load_hazwaste_shp")
G.add_node("hazwaste_gdf", node_type="data", data_path="", description="GeoDataFrame of North Carolina hazardous waste sites")
G.add_edge("load_hazwaste_shp", "hazwaste_gdf")

G.add_node("load_tract_pop", node_type="operation", description="Load North Carolina tract population data")
G.add_edge("nc_tract_pop_csv_url", "load_tract_pop")
G.add_node("tract_pop_df", node_type="data", data_path="", description="DataFrame of North Carolina tract population")
G.add_edge("load_tract_pop", "tract_pop_df")

G.add_node("spatial_join", node_type="operation", description="Perform spatial join between tracts and hazardous waste sites")
G.add_edge("tract_gdf", "spatial_join")
G.add_edge("hazwaste_gdf", "spatial_join")
G.add_node("tracts_with_hazwaste", node_type="data", data_path="", description="GeoDataFrame of tracts containing hazardous waste sites")
G.add_edge("spatial_join", "tracts_with_hazwaste")

G.add_node("join_pop_data", node_type="operation", description="Join population data to tracts with hazardous waste")
G.add_edge("tracts_with_hazwaste", "join_pop_data")
G.add_edge("tract_pop_df", "join_pop_data")
G.add_node("pop_in_hazwaste_tracts", node_type="data", data_path="", description="Population in tracts with hazardous waste sites")
G.add_edge("join_pop_data", "pop_in_hazwaste_tracts")

G.add_node("compute_total_pop", node_type="operation", description="Compute total population in tracts with hazardous waste")
G.add_edge("pop_in_hazwaste_tracts", "compute_total_pop")
G.add_node("total_pop_hazwaste", node_type="data", data_path="", description="Total population living in tracts with hazardous waste")
G.add_edge("compute_total_pop", "total_pop_hazwaste")


G.add_node("create_choropleth_map", node_type="operation", description="Generate population choropleth map, highlighting tracts with hazardous waste")
G.add_edge("tract_gdf", "create_choropleth_map")
G.add_edge("tract_pop_df", "create_choropleth_map")
G.add_edge("tracts_with_hazwaste", "create_choropleth_map")
G.add_node("choropleth_map", node_type="data", data_path="", description="Generated choropleth map")
G.add_edge("create_choropleth_map", "choropleth_map")


#nx.write_graphml(G, "C:\\Users\\chait\\Projects\\LLM_Geo_GCP\\Resident_at_risk_counting\\Resident_at_risk_counting.graphml")