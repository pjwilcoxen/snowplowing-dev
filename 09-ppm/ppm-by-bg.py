"""
ppm-by-bg.py
May 2025 PJW

Compute priority variables and aggregate to BGs.
"""

import pandas as pd
import quicklog
import matplotlib.pyplot as plt

pd.options.mode.copy_on_write = True
stem = 'ppm-by-bg'

ql = quicklog.logger(f'{stem}.log')

#========================================================================
#  Configuration
#
#  ppm_file:  Input file with points per mile by BG and hour
#  out_pkl:   Output file of BGs with priority variables
#  out_dta:   Stata file to create
#  my_event:  Event to keep
#========================================================================

ppm_file = 'ppm-by-hour.pkl'
out_csv = f'{stem}.csv'
out_dta = f'{stem}.dta'
my_event = 1

#========================================================================
#  Start processing
#========================================================================

ql.log('PPM by hour file',ppm_file)
ql.log('CSV output file',out_csv)
ql.log('DTA output file',out_dta)
ql.log('Event to keep',my_event)

#========================================================================
#  Read the input data
#========================================================================

clean = pd.read_pickle(ppm_file)
ql.log('Input records',f"{len(clean):,d}")

#========================================================================
#  Trim to event 1
#========================================================================

ql.log('Event records',clean['event'].value_counts())

is_keeper = clean['event'] == my_event

trim = clean[ is_keeper ]
ql.log(f'Retained records for event {my_event}',len(trim))

for c in ['GEOID','eventhr','District']:
    grouped = trim.groupby(c)
    agg = grouped['count'].agg(['size','sum'])
    ql.log(f'Records and points by {c}',agg)

#========================================================================
#  Make GEOID and the date variables the index and sort it
#========================================================================

trim = trim.set_index(['GEOID','localday','localhr','eventhr'])
trim = trim.sort_index()

assert trim.index.is_unique

#============================================================================
#  Get fixed attributes of BGs (match corresponding basebg variables)
#============================================================================

not_fixed = ['localday','localhr','event','eventhr','count','ppm']

bginfo = trim.reset_index().drop(columns=not_fixed).drop_duplicates()
bginfo = bginfo.set_index('GEOID')

#========================================================================
#  Build cumulative series of counts and points per mile for each BG.
#  Only need one shr variable since ppm is a scaled version of count
#========================================================================

by_geoid = trim.groupby('GEOID')

acc = by_geoid[['count','ppm']].cumsum()

total = by_geoid['count'].sum()
acc['shr'] = acc['count']/total

#========================================================================
#  For reference, compute total plowing by hour
#========================================================================

tot_by_hr = pd.DataFrame()
tot_by_hr['count'] = trim.groupby('eventhr')['count'].sum()
tot_by_hr['accum'] = tot_by_hr['count'].cumsum()
tot_by_hr['shr'] = tot_by_hr['accum']/tot_by_hr['count'].sum()

#========================================================================
#  Find the hour closest to the median
#========================================================================

med_diff = (tot_by_hr['shr']-0.5)**2
med_time = med_diff.nsmallest(1).reset_index().iloc[0]
med_time = med_time['eventhr']

ql.log('Median hour for all plowing',med_time)

#========================================================================
#  Draw a figure
#========================================================================

max_count = tot_by_hr['count'].max()

fig,ax = plt.subplots(dpi=300)
tot_by_hr['count'].plot(title='Total plow points',ax=ax)
ax.axvline(med_time,c='r')
ax.set_xlabel('Event hour')
ax.annotate('50%',
            xy=(med_time,max_count*0.95),
            bbox={'fc':'w'},
            va='center',ha='center'
            )
fig.tight_layout()
fig.savefig('fig-tot-count.png')

#
#  Figure out when each BG hits selected plowing thresholds.
#  Do this by finding the first hour at which the share of the total
#  count exceeds the threshold.
#

res = {}
for level in [0.25, 0.50, 0.75]:
    above = acc[ acc['shr'] > level ].reset_index()
    time = above.groupby('GEOID')['eventhr'].min()
    hr = f'hr{int(level*100)}'
    res[hr] = time

#
#  Combine the results into a single dataframe with one column
#  for each threshold.
#

comb = pd.concat(res)
comb = comb.reset_index()
comb = comb.rename(columns={'level_0':'level'})

hrs = comb.pivot(index='GEOID',columns='level',values='eventhr')

#========================================================================
#  Compute early measure
#========================================================================

#
#  Group GEOIDs by whether they reach each threshold before or after 
#  the median time for that threshold. If they are always early, they
#  will have a score of 3, if always late, a score of 0.
#

medians = hrs.median()
medians.name = 'median'

aug = comb.merge(medians,left_on='level',right_index=True)

aug['early'] = aug['eventhr'] < aug['median']

early = aug.groupby('GEOID')['early'].sum()

ql.log('Early counts',early.value_counts())

#
#  Add it to the BG table
#

bginfo['early'] = early

#============================================================================
#  Find fraction complete at the overall median hour. A little involved
#  to deal with some BGs that have no plowing right at med_time.
#============================================================================

hr = int(med_time)+1

acc_eventhr = acc.reset_index('eventhr')[['eventhr','shr']]
acc_bhi = acc_eventhr[ acc_eventhr['eventhr'] <= med_time ]
acc_bhi_bybg = acc_bhi.sort_values('eventhr',ascending=False).groupby('GEOID')
acc_mm = acc_bhi_bybg.nth(0)

acc_mm = acc_mm.reset_index(['localday','localhr'])[['eventhr','shr']]

assert acc_mm.duplicated().any() == False

acc_mm = acc_mm.rename( columns={
    'eventhr': f'hr_near_{hr}',
    'shr': f'shr_by_{hr}'
    })

#============================================================================
#  Add measures onto BG information
#============================================================================

tot = acc.groupby('GEOID')[['count','ppm']].max()

both = bginfo.join(tot)
both = both.join(hrs)
both = both.join(acc_mm)

#============================================================================
#  Add comparison with snowfall fractions (from weather data)
#============================================================================
#

s25 = 34
s50 = 39
s75 = 45

both['d25'] = both['hr25'] - s25
both['d50'] = both['hr50'] - s50
both['d75'] = both['hr75'] - s75

both['dav'] = both[['d25','d50','d75']].abs().sum(axis='columns')/3

#============================================================================
# Write out a dataset
#============================================================================

both.to_csv(out_csv)
both.to_stata(out_dta)

ql.log('Wrote output files',[out_csv,out_dta],json=True)
