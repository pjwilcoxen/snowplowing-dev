#! /bin/python3
#  Spring 2022 PJW
#
#  Use the Census API to collect information listed in an
#  accompanying input file.
#

import requests
import pandas as pd
import os

#
#  Configure the run
#

ifile = 'input-variables.csv'
ofile = "demography.csv"

acs_yr = 2019
geo = 'bgs'
state_fips = '36'
county_fips = '067'

#
#  Make a subdirectory for individual tables
#

if not os.path.exists('raw'):
    os.mkdir('raw')

#
#  Set up the API information
#    


api = f'https://api.census.gov/data/{acs_yr}/acs/acs5'

in_clause = f'county:{county_fips} state:{state_fips}'

var_info = pd.read_csv(ifile)
var_info = var_info.dropna(subset=['UniqueID'])
var_info['table'] = var_info['Table ID']
var_info['variable'] = var_info['UniqueID']+'E'

for_clause = 'block group:*'
    
#
#  Now get the data table by table
#

grps = var_info.groupby('table')
files = []

for table,table_info in grps:
    
#
#  Get the names of the variables and build a string of 
#  variable names that can be passed to the Census API.
#

    var_name = table_info['variable'].to_list()
    var_list = ['NAME']+var_name
    var_string = ','.join(var_list)

    payload = {'get':var_string,'for':for_clause,'in':in_clause}

    #
    #  Make the API call and check whether an error code was 
    #  returned.
    #

    response = requests.get(api,payload)

    if response.status_code == 200 :
        print('Request successful')
    else:
        print('Returned status:',response.status_code)
        print('Returned text:',response.text)
        assert False 

    #
    #  The results are in JSON. Parse the JSON into a Python object. 
    # It will be a list of rows, each of which is itself a list.
    #

    row_list = response.json()

    #
    #  The first row is the column names and the remaining rows are the data.
    #

    colnames = row_list[0]
    datarows = row_list[1:]

    #
    #  Build a Pandas dataframe and a geoid field
    #

    data = pd.DataFrame(columns=colnames,data=datarows)

    st = data['state']
    co = data['county']
    tr = data['tract']
    bg = data['block group']
    
    data['geoid'] = st+co+tr+bg
    
    data['table'] = table.lower()

    data = data.set_index('geoid')
    
    #  
    #  Warn about empty variables
    #
    
    ndrop = 0
    for v in var_name:
        if data[v].isna().all():
            print(f'Warining: {v} has no data and was dropped')
            data = data.drop(columns=v)
            ndrop += 1

    #
    #  Write out the results.
    #

    if len(var_name) == ndrop:
        print(f'Warning: no remaining variables for {table} so no file written.')
    else:            
        fname = f'raw/{table.lower()}-{geo}.csv'
        data.to_csv(fname)
        files.append( fname )
 
#
#  Now read the files we just built and combine them into one
#  file for each geography
#

merged = pd.DataFrame()

for f in files:
    print('Merging file',f)
    this = pd.read_csv(f,dtype=str)
    this = this.drop(columns=['NAME','state','county','tract','table'])
    this = this.drop(columns="block group")
    if len(merged) == 0:
        merged = this
    else:
        merged = merged.merge(this,how='outer',on='geoid',validate='1:1',indicator=True)    
        check = merged['_merge'].value_counts()
        if check['left_only']>0 or check['right_only']>0:
            print('Warning: unexpected merge result')
            print(check)
        merged = merged.drop(columns='_merge')

#
#  Now convert missing values
#

merged = merged.replace('-666666666', None)

map_names = {
    'B02001_001E': 'pop',
    'B02001_002E': 'pop_white',
    'B25002_001E': 'units',
    'B25002_002E': 'units_occ',
    'B19013_001E': 'med_inc',
}

sel = merged[map_names.keys()].rename(columns=map_names).astype(float)
sel['geoid'] = merged['geoid']

res = sel[['geoid', 'pop', 'units', 'med_inc']].copy()
res['shr_poc'] = (1-sel['pop_white']/sel['pop']).round(4)
res['shr_occ'] = (sel['units_occ']/sel['units']).round(4)

res.to_csv(ofile, index=False)
