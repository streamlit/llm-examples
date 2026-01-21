# Simulate a geospatial heatmap and predictive simulation for the enhanced dashboard

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Mock data for regions with adherence rates and infection projections
regions = {
    "Region A": {"adherence": 85, "projected_infection": 5, "lat": 0.1, "lon": 36.8},
    "Region B": {"adherence": 78, "projected_infection": 10, "lat": 1.3, "lon": 36.9},
    "Region C": {"adherence": 65, "projected_infection": 25, "lat": -1.5, "lon": 37.1},
    "Region D": {"adherence": 90, "projected_infection": 2, "lat": 0.8, "lon": 37.3},
}

# Convert mock data into a GeoDataFrame
data = {
    "Region": list(regions.keys()),
    "Adherence": [regions[reg]["adherence"] for reg in regions],
    "Projected_Infection": [regions[reg]["projected_infection"] for reg in regions],
    "Latitude": [regions[reg]["lat"] for reg in regions],
    "Longitude": [regions[reg]["lon"] for reg in regions],
}
gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data["Longitude"], data["Latitude"]))

# Set up map plotting with adherence heatmap
fig, ax = plt.subplots(1, 2, figsize=(16, 8))

# Heatmap for adherence rates
cmap = ListedColormap(["red", "orange", "green"])
categories = [65, 75, 100]  # Categories for adherence
adherence_colors = ["red" if x < 70 else "orange" if x < 80 else "green" for x in gdf["Adherence"]]

gdf.plot(ax=ax[0], color=adherence_colors, markersize=100, edgecolor="black")
ax[0].set_title("Geospatial Adherence Rates", fontsize=14)
for x, y, label in zip(gdf["Longitude"], gdf["Latitude"], gdf["Region"]):
    ax[0].text(x + 0.05, y, label, fontsize=10)

# Predicted Infection Simulation Bar
ax[1].bar(gdf["Region"], gdf["Projected_Infection"], color="blue")
ax[1].set_title("Predicted Infection Rate Increase (6 Months)", fontsize=14)
ax[1].set_ylabel("Predicted Increase (%)", fontsize=12)
for i, val in enumerate(gdf["Projected_Infection"]):
    ax[1].text(i, val + 1, f"+{val}%", ha="center", fontsize=10)

# Overall Layout
plt.suptitle("ImpactLens AI: Enhanced Geospatial & Predictive Insights", fontsize=16, weight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.95])

plt.show()
