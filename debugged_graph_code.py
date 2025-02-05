import networkx as nx

G = nx.DiGraph()

# Data Nodes
G.add_node("NC_tract_boundary_shp_url", node_type="data", data_path="https://github.com/gladcolor/LLM-Geo/raw/master/overlay_analysis/tract_37_EPSG4326.zip", description="North Carolina tract boundary shapefile URL")
G.add_node("NC_hazwaste_shp_url", node_type="data", data_path="https://github.com/gladcolor/LLM-Geo/raw/master/overlay_analysis/HW_Sites_EPSG4326.zip", description="North Carolina hazardous waste sites shapefile URL")
G.add_node("NC_tract_pop_csv_url", node_type="data", data_path="https://github.com/gladcolor/LLM-Geo/raw/master/overlay_analysis/NC_tract_population.csv", description="North Carolina tract population CSV file URL")
G.add_node("NC_tracts_gdf", node_type="data", data_path="", description="GeoDataFrame of North Carolina tracts")
G.add_node("NC_hazwaste_gdf", node_type="data", data_path="", description="GeoDataFrame of North Carolina hazardous waste sites")
G.add_node("NC_tract_pop_df", node_type="data", data_path="", description="DataFrame of North Carolina tract population")
G.add_node("tracts_with_hazwaste", node_type="data", data_path="", description="GeoDataFrame of tracts containing hazardous waste")
G.add_node("population_in_hazwaste_tracts", node_type="data", data_path="", description="Population in tracts with hazardous waste")
G.add_node("pop_choropleth_map", node_type="data", data_path="", description="Population choropleth map")

# Operation Nodes
G.add_node("load_tract_shp", node_type="operation", description="Load North Carolina tract shapefile")
G.add_node("load_hazwaste_shp", node_type="operation", description="Load North Carolina hazardous waste shapefile")
G.add_node("load_tract_pop_csv", node_type="operation", description="Load North Carolina tract population CSV")
G.add_node("spatial_join", node_type="operation", description="Perform spatial join between tracts and hazardous waste sites")
G.add_node("calculate_total_pop", node_type="operation", description="Calculate total population in tracts with hazardous waste")
G.add_node("create_choropleth_map", node_type="operation", description="Create population choropleth map, highlighting tracts with hazardous waste")

# Edges
G.add_edge("NC_tract_boundary_shp_url", "load_tract_shp")
G.add_edge("load_tract_shp", "NC_tracts_gdf")
G.add_edge("NC_hazwaste_shp_url", "load_hazwaste_shp")
G.add_edge("load_hazwaste_shp", "NC_hazwaste_gdf")
G.add_edge("NC_tract_pop_csv_url", "load_tract_pop_csv")
G.add_edge("load_tract_pop_csv", "NC_tract_pop_df")
G.add_edge("NC_tracts_gdf", "spatial_join")
G.add_edge("NC_hazwaste_gdf", "spatial_join")
G.add_edge("spatial_join", "tracts_with_hazwaste")
G.add_edge("tracts_with_hazwaste", "calculate_total_pop")
G.add_edge("NC_tract_pop_df", "calculate_total_pop")
G.add_edge("calculate_total_pop", "population_in_hazwaste_tracts")
G.add_edge("NC_tracts_gdf", "create_choropleth_map")
G.add_edge("tracts_with_hazwaste", "create_choropleth_map")
G.add_edge("NC_tract_pop_df", "create_choropleth_map")
G.add_edge("create_choropleth_map", "pop_choropleth_map")

# Example of accessing node attributes
# print(G.nodes["NC_tract_boundary_shp_url"])

# Write the graph to a GraphML file
# Uncomment the following line to save the graph
nx.write_graphml(G, "C:\\Users\\chait\\Projects\\LLM_Geo_GCP\\Resident_at_risk_counting\\Resident_at_risk_counting.graphml")
