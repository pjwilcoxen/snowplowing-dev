# About these files

## bg_districts_final.csv

`bg_districts_final.csv` is an exported table of block group snowplow districts that we constructed from spatial data in ArcGIS using the following source layers and geoprocessing tools.

### Source Layers

SnowPlowDistricts_Final_120618.shp contains polygon boundaries of snowplow districts in Syracuse City.

tl_2018_36_bg.shp is a Topologically Integrated Geographic Encoding and Referencing (TIGER) file containing the polygon boundaries of census block groups in New York State.

tl_2018_36_place.shp is a TIGER file containing the polygon boundaries of census incorporated places in New York State.
Geoprocessing Tools
To prepare the original snowplow districts layer (SnowPlowDistricts_Final_120618), we put it into a coordinate system suitable for local spatial analysis using Project (Data Management Tools).  Then we aggregated the parts of the districts at the district level using Dissolve (Data Management Tools).

We prepared the source block group layer by selecting Syracuse from tl_2018_36_place.shp and using the output layer to clip tl_2018_36_bg.shp. We projected the Syracuse block group layer in same coordinate system as the snowplow districts layer. There are 135 records in the Syracuse block group layer.

We joined the snowplow districts to the block groups using Spatial Join (Analysis Tools) with the Match Option set to Largest overlap. We retained the field GEOID from the target, block group layer and the field District from the join features, snowplow district layer.

## bg_variables_final.csv

TBD
