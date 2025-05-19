"""
bg-merge.py
Mar 2025 PJW

Merge BG information.
"""

import pandas as pd
import quicklog 

ql = quicklog.logger('bg-merge.log')

#  Output files

outcsv = 'bg-merge.csv'
outpkl = 'bg-merge.pkl'

#  Input files

base_file = "bg_variables_final.csv"
dist_file = "bg_districts_final.csv"
demo_file = "demography.csv"

#  BG not plowed or in a plow district

not_plowed = '360670132002'

#%%
#
#  Read the base BG data file
#

ql.log('Base file',base_file)
base = pd.read_csv(base_file,dtype=str)
base = base.drop(columns='OBJECTID')
ql.log('Rows',len(base))
ql.log('Variables',sorted(base.columns),json=True)

#
#  Merge in the demographic information. Use a left join since the 
#  demographic data is for the whole county rather than the city
#

ql.log('Demography file',demo_file)
demo = pd.read_csv(demo_file,dtype=str)
demo = demo.rename(columns={'geoid':'GEOID'})
ql.log('Rows',len(demo))
ql.log('Variables',sorted(demo.columns),json=True)

merged1 = base.merge(demo,on='GEOID',how='left')
assert len(merged1) == len(base)

#%%
#
#  Read the district information
#

ql.log('District file',dist_file)
dist = pd.read_csv(dist_file,dtype=str)
dist = dist.drop(columns='OBJECTID')
ql.log('BGs with districts',dist['District'].count())

#
#  Combine them
#

merged2 = merged1.merge(dist,on='GEOID',how='outer',validate='1:1')
assert len(merged2) == len(base)

ql.log('Expected BG not in a district',not_plowed)

no_dist = merged2[ merged2['District'].isna() ]
ql.log('BGs without districts',no_dist['GEOID'])

assert len(no_dist)==1 and no_dist.iloc[0]['GEOID']==not_plowed

#%%
#
#  Write out the result  
#

merged2.to_csv(outcsv,index=False)

bginfo = merged2.set_index('GEOID')
bginfo = bginfo.astype(float)
bginfo.to_pickle(outpkl)

ql.log('Variables written',sorted(bginfo.columns),json=True)

ql.log('Files written',[outcsv,outpkl],json=True)
