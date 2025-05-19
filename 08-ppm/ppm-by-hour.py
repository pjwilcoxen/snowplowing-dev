"""
ppm-by-hour.py
May 2025 PJW

Read plow data, join on block group GEOIDs, and then count plow points per
block group in each hour. Don't aggregate to BGs yet: that will be done in
the priority.py script.
"""

import pandas as pd
import quicklog

pd.options.mode.copy_on_write = True
stem = 'ppm-by-hour'

ql = quicklog.logger(f'{stem}.log')

#========================================================================
#  Initial setup
#
#  plow_file:  Input file with plow points by BG and hour
#  bg_file:    Input file with BG attributes
#  out_pkl:    Output file with plow points per mile
#========================================================================

plow_file = 'points-by-bg-hour.pkl'
bg_file = 'bg-merge.pkl'
out_pkl = f'{stem}.pkl'

ql.log('Plow point data',plow_file)
ql.log('BG data',bg_file)
ql.log('Output file',out_pkl)

#========================================================================
#  Block groups to filter out
#========================================================================

drop_blocks = {
    '360670036011': 'Depot',
    '360670132001': 'Less than 0.1 miles',
    '360670132002': 'Not plowed',
}

ql.log('Block groups to drop',drop_blocks,json=True)

#========================================================================
#  Read the plow point data. One record per BG per hour.
#========================================================================

raw_counts = pd.read_pickle(plow_file)
ql.log('Total records',f"{len(raw_counts):,d}")

#
#  Report number of unique BGs
#

bg_count = len(raw_counts['GEOID'].unique())
ql.log('Block groups',bg_count)

#
#  Report number of unique events and hours
#

events_hrs = ( raw_counts[['event','eventhr']]
              .drop_duplicates()
              .groupby('event')
              .size() )

ql.log('Events and hours',events_hrs)

#
#  Report total number of plow points
#

tot_points = raw_counts['count'].sum()
ql.log('Total plow points',f"{tot_points:,d}")

#========================================================================
#  Read the BG data
#========================================================================

bg_raw = pd.read_pickle(bg_file)
ql.log('Raw BG block groups',len(bg_raw))

bg_trim = bg_raw.drop( drop_blocks.keys() )
ql.log('Trimmed BG block groups',len(bg_trim))

assert len(bg_raw) == (len(bg_trim)+len(drop_blocks))

#========================================================================
#  Merge BG information onto the plow data.
#  Do it as a right join to discard the depot and small BGs.
#========================================================================

counts = raw_counts.merge(bg_trim,left_on='GEOID',right_index=True,
                          how='right',validate='m:1',
                          indicator=True)

#
#  Check the merge: should all be in both
#

check = counts['_merge'].value_counts()
ql.log('Join of BGs onto points',check)

assert check['right_only'] == 0 and check['left_only'] == 0
ql.log('Join status','OK')

clean = counts.drop(columns=['_merge'])

#========================================================================
#  Compute PPM
#========================================================================

clean['ppm'] = clean['count']/clean['city_miles']

#========================================================================
#  Done: save the results
#========================================================================

clean.to_pickle(out_pkl)
ql.log('Saved PPM by hour data',out_pkl)
