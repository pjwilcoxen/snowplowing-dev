"""
snowplow.py
Mar 2025 PJW

Read the city's snowplow data and build a consistent dataset.
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import quicklog
import datetime

#
#  Open the logger
#

ql = quicklog.logger('snowplow.log')

#
#  Names of the output files
#

output_csv  = 'snowplow_trim.csv'
output_pkl  = 'snowplow_trim.pkl'
output_gpkg = 'snowplow_trim.gpkg'

#
#  Location and names of input files. Each input file is shown in 
#  a tuple with the ID number of the event.
#

rawdir = '../01-plow-data/'

csv_files = [("Snowplow_Data_January_1_2018.csv",2),
             ("Snowplow_Data_January_2_2018.csv",2),
             ("Snowplow_Data_January_3_2018.csv",2),
             ("Snowplow_Data_January_4_2018.csv",2),
             ("Snowplow_Data_January_7_2018.csv",3),
             ("Snowplow_Data_January_8_2018.csv",3),
             ("Snowplow_Data_January_9_2018.csv",3),
             ("Snowplow_Data_March_13_2017.csv" ,1),
             ("Snowplow_Data_March_14_2017.csv" ,1),
             ("Snowplow_Data_March_15_2017.csv" ,1),
             ("Snowplow_Data_March_16_2017.csv" ,1)]

#
#  Read the data
#

data = []
for file,event in csv_files:
    ql.log(f'Input file, event {event}',file)
    raw = pd.read_csv(rawdir+file,dtype=str)
    raw = raw.apply(lambda x: x.str.strip())
    
    trim = pd.DataFrame()
    for c in ['latitude','longitude','truck_name','activity_type']:
        trim[c] = raw[c]
        trim['ts_utc'] = pd.to_datetime(raw['date_fixed'])
        trim['event'] = event
        
    data.append( trim )

#%%
#
#  Append the datasets
#

comb = pd.concat(data,ignore_index=True)
comb = comb.sort_values(['ts_utc','truck_name'])

#%%
#
#  Build a local timestamp and the eventhr variable, which measures
#  how far we are into an event
#

comb['ts_local'] = comb['ts_utc'].dt.tz_convert('US/Eastern')

#
#  Round to the nearest hour and build some user-friendly 
#  variables showing the day and hour of the event
#

comb['hr_local'] = comb['ts_local'].dt.round(freq='h')

comb['localhr'] = comb['hr_local'].dt.hour
comb['localday'] = comb['hr_local'].dt.strftime('%Y-%m-%d')

#
#  Now build the elapsed time indicator eventhr
#

comb = comb.set_index('event')

e_start = comb.groupby('event')['hr_local'].min()
td_hour = datetime.timedelta(hours=1)

comb['eventhr'] = (comb['hr_local'] - e_start)/td_hour
comb['eventhr'] = comb['eventhr'].astype(int)

comb = comb.reset_index() 

#%%
#
#  Remove duplicates. Very few when activit_type is present but 
#  a few more after we drop that
#

n_last = len(comb)
comb = comb.drop_duplicates()
n_drop = n_last - len(comb)

ql.log('Duplicates eliminated before dropping activity type',n_drop)

comb = comb.drop(columns='activity_type')

n_last = len(comb)
comb = comb.drop_duplicates()
n_drop = n_last - len(comb)

ql.log('Duplicates eliminated after dropping activity type',n_drop)

#%%
#
#  Look for idling trucks. Consider a truck to be idling if it there are 
#  duplicate entries for it at the exact same coordinates in a given 
#  event hour.
#

truck_loc = ['event','eventhr','truck_name','latitude','longitude']

n_last = len(comb)
comb = comb.drop_duplicates(subset=truck_loc)
n_drop = n_last - len(comb)

ql.log('Duplicates eliminated after dropping idlers',n_drop)

ql.log('Final number of records',len(comb))

#%%
#
#  Build a geodatabase using the coordinates
#

epsg_pro = 4269 

comb['latitude']  = comb['latitude'].astype(float)
comb['longitude'] = comb['longitude'].astype(float)

points = [Point(xy) for xy in zip(comb['longitude'],comb['latitude'])]

gdf = gpd.GeoDataFrame(comb,geometry=points)
gdf = gdf.set_crs(epsg_pro)

#%% 
#
#  Write the results out in several formats
#

ql.log('Variables',sorted(comb.columns),json=True)

comb.to_csv(output_csv,index=False)
ql.log('Output file',output_csv)

comb.to_pickle(output_pkl)
ql.log('Output file',output_pkl)

gdf.to_file(output_gpkg,layer='points',driver='GPKG')
ql.log('Output file',output_gpkg)

#%%

ql.close()
