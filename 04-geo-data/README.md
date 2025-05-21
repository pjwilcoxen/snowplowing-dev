# About these files

## bg_districts_final.csv

`bg_districts_final.csv` is an exported table of block group snowplow districts that we constructed from spatial data in ArcGIS using the following source layers and geoprocessing tools.

### Source Layers

* `SnowPlowDistricts_Final_120618.zip` contains polygon boundaries of snowplow districts in Syracuse City.

* `tl_2018_36_bg.zip` is a Topologically Integrated Geographic Encoding and Referencing (TIGER) file containing the polygon boundaries of census block groups in New York State.

* `tl_2018_36_place.zip` is a TIGER file containing the polygon boundaries of census incorporated places in New York State.

### Geoprocessing Tools

To prepare the original snowplow districts layer (`SnowPlowDistricts_Final_120618.zip`), we put it into a coordinate system suitable for local spatial analysis using Project (Data Management Tools).[^1]  Then we aggregated the parts of the districts at the district level using Dissolve (Data Management Tools).

We prepared the source block group layer by selecting Syracuse from `tl_2018_36_place.zip` and using the output layer to clip `tl_2018_36_bg.zip`. We projected the Syracuse block group layer in same coordinate system as the snowplow districts layer. There are 135 records in the Syracuse block group layer.

We joined the snowplow districts to the block groups using Spatial Join (Analysis Tools) with the Match Option set to Largest overlap. We retained the field `GEOID` from the target, block group layer and the field `District` from the join features, snowplow district layer.[^2]

## bg_variables_final.csv

`bg_variables_final.csv` is an exported table of block group attributes that we constructed from spatial data in ArcGIS using the following source layers and variable definitions.

### Source Layers

* `tl_2018_36_bg.zip` is a Topologically Integrated Geographic Encoding and Referencing (TIGER) file containing the polygon boundaries of census block groups in New York State.

* `tl_2018_36_place.zip` is a TIGER file containing the polygon boundaries of census incorporated places in New York State.

* `Syracuse_Streeets_2016.zip` is line file of Syracuse City street segments.

* `Emergency_Snow_Routes.zip` is a line file of Syracuse City street segments that are designated emergency.

* `Rush_Hour_Routes.zip` is a line file of Syracuse City street segments that are designated rush hour.

* `Parcel_Map_Q1_2020.zip` is a polygon tax parcel dataset for Syracuse City.

* `VW_BRIDGES.gdb` is a point file inventory of bridges in New York State.

* `USGS_13_n43w077_20230227.tif` is a Digital Elevation Model (DEM) raster tile covering the southern portion of Syracuse.

* `USGS_13_n44w077_20230227.tif` is a DEM raster tile covering the northern portion of Syracuse.

### Variables

#### `priority_miles`

The total mileage of Syracuse City priority streets by block group.

1. We put each source layer (Emergency_Snow_Routes.shp and Rush_Hour_Routes.shp) into a common coordinate system using Project (Data Management Tools).[^3]

2. We merged the source layers, creating a single priority streets layer. The merged file had 6,519 records, many of which were duplicates.

3. We eliminated duplicate shapes and segment IDs with Delete Identical (Data Management Tools), reducing the records to 2,488 priority street segments.

4. In the priority streets layer, we created the field miles and used Calculate Geometry to add length information (in miles) to each priority street segment.

5. We prepared the source block group layer by selecting Syracuse from tl_2018_36_place.shp and using the output layer to clip tl_2018_36_bg.shp. We projected the Syracuse block group layer in same coordinate system as the priority streets layer. There are 135 records in the Syracuse block group layer.

6. We used the clipped and projected block group layer in conjunction with the priority streets layer, and, with Tabulate Intersection (Analysis Tools), we summed up the mileage of priority street segments for each block group. There are 132 records in the output table.

7. We created the field priority_miles in the block group attributes. We joined the miles field from the Tabulate Intersection output table to the block group layer based on GEOID. 3 records in the block group layer were null for miles. We selected miles is null and calculated the selected records miles = 0. Then we used the miles values to populate priority_miles, and we deleted the field miles.

#### city_miles

The total mileage of Syracuse City streets by block group.

1. We projected the source layer Syracuse_Streeets_2016.shp into the same coordinate system as the Syracuse block group layer.

2. Syracuse_Streeets_2016.shp has duplicate records for street segments. We dropped duplicate shapes and segment IDs using Delete Identical. This reduced the number of records from 25,421 to 7,161.

3. Syracuse_Streeets_2016.shp contains interstate highways, for which the city snow removal fleet is not responsible. We selected highway number 481 or 81 or 690 and used Delete Features (Data Management Tools), further reducing the number of records to 6,764.

4. In the edited streets layer, we created the field miles and used Calculate Geometry to add length information (in miles) to each street segment.

5. Then we ran the Tabulate Intersection tool on the block group layer and the street layer in order to sum up the mileage of street segments for each block group.

6. We created the field city_miles in the block group attributes. We joined the miles field from the Tabulate Intersection output table to the block group layer based on GEOID. Then we used the miles values to calculate city_miles, and we deleted the field miles.

#### priority_fraction

The fraction of the city street miles that are priority by block group. We created a new field in the block group layer called priority_fraction. This field is calculated priority_miles / city_miles.

#### SUM_res_sq_miles

The sum of residential parcel area (square miles) by block group.

1. We projected Parcel_Map_Q1_2020.shp into the same coordinate system as the Syracuse block group layer.

2. We ran Spatial Join (Analysis Tools), Match Option “Have their center in,” on parcels (target features) and block groups (join features), joining block groups attributes to parcel shapes.

3. We added the field res_sq_miles to the attributes of the joined layer. We selected the residential properties, 200 class parcels (210-281) and used Calculate Geometry to get the area in square miles for the field res_sq_miles.

4. We used Summary Statistics (Analysis Tools) on the joined layer and summed up the res_sq_miles field by block group GEOID.

5. Then we joined the SUM_res_sq_miles field from the statistics table to the block group layer. We selected SUM_res_sq_miles is null and calculated the selected records as 0.

#### SUM_sq_miles

The sum of parcel area (square miles) by block group.

1. We added the field `sq_miles` to the attributes of the joined parcel and block group layer. We used Calculate Geometry to get the area in square miles for the field sq_miles.

2. We used Summary Statistics on the joined layer and summed up the sq_miles field by block group `GEOID`.

3. Then we joined the `SUM_sq_miles` field from the statistics table to the block group layer.

#### pct_res

The percentage of parcel area that is residential by block group. We created the field pct_res in the block group attributes and calculated `pct_res` = `SUM_res_sq_miles` / `SUM_sq_miles` * 100.

#### mean_grade

The mean grade of the Syracuse City streets by block group.

1. We used Create Mosaic Dataset and Add Rasters To Mosaic Dataset (Data Management Tools) to combine the elevation raster tiles (USGS_13_n43w077_20230227.tif and USGS_13_n44w077_20230227.tif).

2. We ran Zonal Statistics as Table (Spatial Analyst Tools) with our streets layer as zones and the raster mosaic as the value input to get a table of minimum and maximum elevation values (fields MIN and MAX) for each street segment. The vertical units in the source rasters are meters.

3. We created three fields in the zonal statistics output table: min_ft (min_ft = MIN * 3.28084), max_ft (max_ft = MAX * 3.28084), and elev_diff_ft (elev_diff_ft = max_ft – min_ft).

4. We added the field run_ft to the street attributes and calculated the length of the segments in feet. Then we added and calculated grade (grade = elev_diff_ft / run_ft * 100).[^4]

5. We projected the bridge inventory file (VW_BRIDGES.gdb) into the same coordinate system as the street file.

6. We used Near (Analysis Tools) to find the closest bridge to street segments within a search radius of 30 ft. The result is that intersecting segments near bridge locations frequently share the same bridge attributes.

7. In order to differentiate street segments that are carried by a bridge from ones that cross a bridge, we created the field carry_cross in the street attribute table, manually selected each unique bridge ID, and classified the affiliated street segments as either carried or crossed.

8. In the street attributes table, we created the field false_grade and flagged the following street segments: carried streets with grades greater than 6; crossed streets with grades greater than 10; and unclassified streets (not within 30ft of a bridge) with grades greater than 20.

9. In the street attributes table, we selected false_grade is null. Then we ran Summarize Within (Analysis Tools) using the block group layer for polygons and the selected street segments (6,646) for summary features. We chose the field grade and set the statistic type as mean. This created the mean_grade field in the block group attribute table.

#### dangle_miles

The total mileage of dead-end street segments by block group.

1. We took the streets layer and ran the Feature Vertices To Points (Data Management Tools) with the Point Type Dangling vertex. This converts the vertices in line segments to points but retains only “dangles” and their associated line segment attributes.[^5]  Interstate highway ramps were in the dangle output layer because we had removed the connecting interstates from the original street file.

2. We selected the ramps in the dangle attributes and used the Delete Features tool on the selected records (68).

3. We used Tabulate Intersection with block group zones and dangle features to sum up the dangle length by block group. The output file has the field DANGLE_LEN (in feet).

4. We transferred the DANGLE_LEN field from the tabulate intersection table to the block group attributes using Join Field. Null values for DANGLE_LEN were calculated as 0.

5. We created the field dangle_miles in the block group attributes and populated it: dangle_miles = DANGLE_LEN / 5280.

#### dangle_fraction

The fraction of city street miles that are dead ends by block group. dangle_fraction = dangle_miles / city_miles.

[^1]: We chose the State Plane Coordinate System for central New York: NAD_1983_2011_StatePlane_New_York_Central_FIPS_3102_Ft_US.

[^2]: One block group (of 135) does not intersect any snowplow district, so it received null for District. The block group GEOID = 360670132002 is a water supply facility on the western edge of the city.

[^3]: For accuracy calculating distance, we chose the State Plane Coordinate System for central New York: NAD_1983_2011_StatePlane_New_York_Central_FIPS_3102_Ft_US.

[^4]: The DEMs generally show the elevation values of the topography underneath bridges. As such, the bare earth data at bridge locations is not useful for determining bridge grade, which is typically less than the grade of the substructure embankment. Using the NYS Department of Transportation inventory of bridges, we located street segments that have suspected false elevation values and excluded them from the analysis.

[^5]: A dangle is a point at one end of a line that is not connected to another line. Where lines represent streets, dangles represent dead ends.
