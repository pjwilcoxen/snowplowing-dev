"""
plot-snow.py
Jul 2023 PJW

Plot the current and accumulated precipitation for event 1.

Input:
    hourly-2017-03.csv
    noaa-data-us-units.csv

Output:
    plot and log file
    
"""

import pandas as pd
import matplotlib.pyplot as plt
from quicklog import logger

plt.rcParams['figure.dpi'] = 300

hourly_file = 'hourly-2017-03.csv'
daily_file  = 'noaa-data-us-units.csv'

ql = logger('plot-snow.log')
ql.log('Hourly data',hourly_file)
ql.log('Daily data',daily_file)

#
#  Build strings for selecting data
#

mon  = '2017-03'
day1 = f'{mon}-13'
dayN = f'{mon}-16'

ql.log('Day range',f'{day1} to {dayN}')

#
#  Get hourly precipitation, in inches of water
#

hourly_precip = pd.read_csv(hourly_file)

date = hourly_precip['day' ].apply(lambda x: f'{mon}-{x:02d}')
hour = hourly_precip['hour'].apply(lambda x: f'{x-1:02d}')
hourly_precip['DATE'] = date
hourly_precip['ts'] = pd.to_datetime( date+' '+hour )

keep = hourly_precip['DATE'].between(day1,dayN)
hourly_precip = hourly_precip[ keep ]
hourly_precip = hourly_precip.sort_values('ts')
hourly_precip['event_hr'] = range(0,len(hourly_precip))
hourly_precip = hourly_precip.reset_index(drop=True)

#
#  Get daily precipitation and snow fall; keep only the airport since
#  it matches the hourly precipitation data
#

daily_snow = pd.read_csv(daily_file)
daily_snow = daily_snow[ daily_snow['NAME'].str.contains('HANCOCK')]

keep = daily_snow['DATE'].between(day1,dayN)
daily_snow = daily_snow[ keep ]
daily_snow = daily_snow.sort_values('DATE')

#
#  Verify that the daily precipitation totals are the same
#

check_h = hourly_precip.groupby('DATE')['inches'].sum()
check_d = daily_snow.set_index('DATE')[['NAME','PRCP','SNOW']]

check = check_d.join(check_h)
assert (check['PRCP']==check['inches']).all()

ql.log('Daily precipitation, inchces of water',check['inches'])
ql.log('Daily precipitation, inches of snow',check['SNOW'])

#
#  Build a ratio for converting water to snow
#

water_to_snow = check['SNOW'].sum()/check['PRCP'].sum()

ql.log('Conversion, water to snow',water_to_snow)

#
#  Build an hourly snow value
#

hourly_precip['snow'] = hourly_precip['inches']*water_to_snow
hourly_precip['acc'] = hourly_precip['snow'].cumsum()
hourly_precip['accpct'] = hourly_precip['acc']/hourly_precip['acc'].max()

#
#  Find event hr where cumulative snowfall hits critical points
#

ap = hourly_precip['accpct']
for cut in [0.25, 0.5, 0.75]:
    hr = hourly_precip[ ap > cut]['event_hr'].min()
    ql.log(f'Hour for {cut} cutoff',hr)

#%%
#
#  Draw figures
#

fig,(axT,axB) = plt.subplots(2,1,figsize=(4,5),sharex=True)

hourly_precip.plot(x='ts',y='snow',ax=axT,legend=False)
axT.set_title('Hourly Snowfall')
axT.set_ylabel('Inches per Hour')
axT.set_xlabel('')
axT.axvline('2017-03-14',color='gray',lw=1,ls='--')
axT.axvline('2017-03-15',color='gray',lw=1,ls='--')
axT.axvline('2017-03-16',color='gray',lw=1,ls='--')

hourly_precip.plot(x='ts',y='acc',ax=axB,legend=False)
axB.set_title('Cumulative Depth')
axB.set_ylabel('Inches')
axB.set_xlabel('')
axB.axvline('2017-03-14',color='gray',lw=1,ls='--')
axB.axvline('2017-03-15',color='gray',lw=1,ls='--')
axB.axvline('2017-03-16',color='gray',lw=1,ls='--')

fig.tight_layout()
fig.savefig('plot-snow.png')
