"""
plot.py
May 2024 PJW

Plot delay by BG, including fitted and counterfactuals.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

plt.rcParams['figure.dpi'] = 300

#  Read the data

geo = gpd.read_file('syracuse_bg/syracuse_bg.shp')
dat = pd.read_csv('counter.csv',dtype={'GEOID':str})

#  Merge the regression results onto the polygons

merged = geo.merge(dat,on='GEOID',how='outer',indicator=True)
print(merged['_merge'].value_counts())
merged = merged.drop(columns='_merge')

#  Make a county object for a border

county = merged.dissolve()

#%%

#
#  Variables to map
#

cols = ['d25','fit','res','counter','diff']

print(merged[cols].agg(['min','mean','max']))

#  Set the scale and colormaps

vmin = merged['d25'].min()
vmax = merged['d25'].max()

cmap1 = 'RdYlBu_r'
cmap2 = cmap1

#
#  Walk through the variables mapping each one
#

for i,v in enumerate(cols):

    lo = round(merged[v].min(),1)
    hi = round(merged[v].max(),1)

    fig,ax = plt.subplots()
    fig.suptitle(f'Variable {v}')

    if not v in ['diff','res']:
        merged.plot(v,legend=True,cmap=cmap1,vmin=vmin,vmax=vmax,ax=ax)
    else:
        merged.plot(v,legend=True,cmap=cmap2,ax=ax)

    missing = merged[merged[v].isna()]
    missing.boundary.plot(color='gray',linewidth=0.5,ax=ax)
    missing.plot(color='lightgray',ax=ax)

    county.boundary.plot(linewidth=0.5,color='black',ax=ax)

    fig.supxlabel(f'Range: {lo} to {hi}',fontsize='small')
    ax.axis('off')
    fig.tight_layout()
    fig.savefig(f'figs/f{i+1}-{v}.png')
