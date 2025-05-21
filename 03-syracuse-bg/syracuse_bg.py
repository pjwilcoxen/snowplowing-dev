""" 
syracuse.py
Mar 2025 PJW

Select block groups in the City of Syracuse.
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import quicklog

pd.options.mode.copy_on_write = True

ql = quicklog.logger('syracuse_bg.log')

on_fips = '067'
syr_fips = '3673000'
utm18n = 26918

ny_bg_file = 'tl_2019_36_bg.zip'
ny_place_file = 'tl_2019_36_place.zip'
syr_bg_file = 'syracuse_bg.gpkg'
syr_shape = 'syracuse_bg'

ql.log('Block group file',ny_bg_file)
ql.log('Places file',ny_place_file)
ql.log('Output file',syr_bg_file)

ny_bg = gpd.read_file(ny_bg_file)
ny_place = gpd.read_file(ny_place_file)

#%%

on_bg = ny_bg.query(f"COUNTYFP=='{on_fips}'")
on_bg = on_bg.to_crs(utm18n)
on_bg = on_bg.set_index('GEOID')

ql.log('County block groups',len(on_bg))

syr = ny_place.query(f"GEOID=='{syr_fips}'")
syr = syr.to_crs(utm18n)

ql.log('Syracuse places',len(syr))

clip = on_bg.clip(syr,keep_geom_type=True)

ql.log('Selected block groups',len(clip))

#%%

#
#  Chose BGs to keep
#

areas = pd.DataFrame()
areas['on'] = on_bg.area
areas['clip'] = clip.area
areas['pct'] = 100*areas['clip']/areas['on']

keep = areas[ areas['pct']>0 ]

#
#  Show full BGs 
#

syr_bg_list = keep.index
syr_bg = on_bg[ on_bg.index.isin(syr_bg_list) ]
syr_bg['pct'] = areas['pct']

n = len(syr_bg)

fig,ax = plt.subplots()
fig.suptitle(f'Percent of block group overlapped by Syracuse (n={n})')
syr_bg.plot('pct',ax=ax,legend=True)
syr.boundary.plot(ax=ax,color='r',lw=1)
ax.axis('off')
fig.tight_layout()
fig.savefig('fig1-full-bg.png')

syr_bg.to_file(syr_bg_file,layer='full')
ql.log(f'Wrote layer full, {n} block groups',syr_bg_file)

#
#  Show clipped BGs
#

clip['pct'] = areas['pct']

n = len(clip)

fig,ax = plt.subplots()
fig.suptitle(f'Percent of clipped block groups in Syracuse, (n={n})')
clip.plot('pct',ax=ax,legend=True)
syr.boundary.plot(ax=ax,color='r',lw=1)
ax.axis('off')
fig.tight_layout()
fig.savefig('fig2-clip-bg.png')

ql.log('Clipped block groups',len(clip))
ql.log('Percent of original BG',clip['pct'])

clip.to_file(syr_bg_file,layer='clipped')
ql.log(f'Wrote layer clipped, {n} block groups',syr_bg_file)

#
#  Show BGs 100% in the City (excludes two)
#

trim = clip[ clip['pct']> 95 ]

n = len(trim)

fig,ax = plt.subplots()
fig.suptitle(f'Trimmed block groups in Syracuse (n={n})')
trim.plot(ax=ax,legend=True)
syr.boundary.plot(ax=ax,color='r',lw=1)
ax.axis('off')
fig.tight_layout()
fig.savefig('fig3-trim-bg.png')

trim.to_file(syr_bg_file,layer='trimmed')
ql.log(f'Wrote layer trimmed, {n} block groups',syr_bg_file)

trim.to_file(syr_shape)
ql.log('Wrote shapefile',syr_shape)
