"""
Extract hourly precipitation data from converted NOAA PDFs
Jan 2022 PJW
"""

import pandas as pd
import quicklog 

ql = quicklog.logger()

#
#  Set up file names, with days per month
#

files = {
    "hourly-2017-03.xlsx":31,
    }

#
#  Set up a dictionary for mapping column names
#

name_map = {
    'Unnamed: 0': 'day',
    'NOON': '12',
    'MID': '24'
    }

for h in range(1,12):
    name_map[f'{h} AM'] = str(h)
    name_map[f'{h} PM'] = str(h+12)

#
#  Do the work
##
    
for f in files.keys():
    
    ql.log('File',f)
    
    #  Read the file
    
    raw = pd.read_excel(f,header=9,skipfooter=9,dtype=str)
    
    #  Make sure it has expected number of days 
    
    assert len(raw) == files[f]
    
    #  Clean up column names and make sure there are the right number
    
    fix = raw.rename(columns=name_map)
    keepers = [c for c in fix.columns if not c.startswith("Unnamed")]

    fix = fix[ keepers ]
    fix = fix.set_index('day')
    
    assert fix.shape[1] == 24
    
    #  Fill in 0's where appropriate
    
    fix = fix.fillna('0')
    fix = fix.replace({'T':'0'})
    
    #  Stack the data
    
    stk = fix.stack()
    stk.index.rename('hour',level=1,inplace=True)
    stk.name = 'inches'
    
    #  Remove 's' flags
    
    stk = stk.str.replace('s','')
    stk = stk.astype(float)

    #  Say something about what's there

    ql.log('Precipitation counts', stk.value_counts())
    ql.log('Total inches', stk.sum())
    
    #  Save the result
    
    stk.to_csv(f.replace('.xlsx','.csv'))
    
  