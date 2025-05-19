"""
points-by-by-hour.py
Mar 2025 PJW

Read plow data, join on block group GEOIDs, and then count
plow points per block group in each hour.

Input:
    snowplow_trim.gpkg, layer=points
    syracuse_bg.gpkg, layer=clipped

Output:
    points-by-bg-hour.csv
    points-by-bg-hour.pkl
"""

import geopandas as gpd
import quicklog

#
#  Input files
#

point_file = 'snowplow_trim.gpkg'
point_layer = 'points'

bg_file = 'syracuse_bg.gpkg'
bg_layer = 'clipped'

#
#  Output files
#

output_csv  = 'points-by-bg-hour.csv'
output_pkl  = 'points-by-bg-hour.pkl'

#
#  Begin work
#

ql = quicklog.logger('points-by-bg-hour.log')

#
#  Read the input files
#


points = gpd.read_file(point_file,layer=point_layer)
ql.log('Point file',f'{point_file}, layer={point_layer}')
ql.log('Records found',len(points))

bgs = gpd.read_file(bg_file,layer=bg_layer)
ql.log('Block group file',f'{bg_file}, layer={bg_layer}')
ql.log('Records found',len(bgs))

#
#  Reproject points to CRS of bgs (UTM18N)
#

points = points.to_crs( bgs.crs )

#%%
#
#  Find the block group for each plow point. Only keep points that are in
#  the city
#

points_bg = points.sjoin(bgs,how='inner')

points_bg.drop(columns='index_right',inplace=True)

ql.log('Joined records',len(points_bg))

#%%
#
#  Count the plow points by date, time and block group.
#

grouped = points_bg.groupby(['localday','localhr','event','eventhr','GEOID'])

count_by_hour = grouped.size()
count_by_hour.name = 'count'
count_by_hour = count_by_hour.reset_index()

#
#  Write it out
#

count_by_hour.to_csv(output_csv,index=False)
ql.log('Wrote output',output_csv)

count_by_hour.to_pickle(output_pkl)
ql.log('Wrote output',output_pkl)
