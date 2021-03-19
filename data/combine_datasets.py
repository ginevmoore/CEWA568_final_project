import pandas as pd
import numpy as np

# reading in each file, skipping the rows with metadata
turbidity = pd.read_csv('turbidity_OG.dat', delim_whitespace=True, skiprows=28)
temperature = pd.read_csv('temperature-water_OG.dat', delim_whitespace=True, skiprows=30)
gageheight = pd.read_csv('gage-height_OG.dat', delim_whitespace=True, skiprows=28)
discharge = pd.read_csv('discharge_OG.dat', delim_whitespace=True, skiprows=29)

# removing the first row beneath the column names which lists the data type
turbidity = turbidity[turbidity.agency_cd != '5s']
temperature = temperature[temperature.agency_cd != '5s']
gageheight = gageheight[gageheight.agency_cd != '5s']
discharge = discharge[discharge.agency_cd != '5s']

# reducing columns of each dataframe to only the data (removing site name, agency)
turbidity = turbidity[['datetime', '256628_63680_00001', '256628_63680_00001_cd', '256629_63680_00002', '256629_63680_00002_cd', '256630_63680_00008', '256630_63680_00008_cd']]
temperature = temperature[['datetime', '149156_00010_00001', '149156_00010_00001_cd', '149157_00010_00002', '149157_00010_00002_cd', '149158_00010_00003', '149158_00010_00003_cd']]
gageheight = gageheight[['datetime', '149155_00065_00003', '149155_00065_00003_cd']]
discharge = discharge[['datetime', '149154_00060_00003', '149154_00060_00003_cd']]

# renaming columns to be more meaningful/easy to use for analysis
turbidity.rename(columns = {'256628_63680_00001':'max_turbidity', '256628_63680_00001_cd':'max_turbidity_cd','256629_63680_00002':'min_turbidity', '256629_63680_00002_cd':'min_turbidity_cd','256630_63680_00008':'med_turbidity', '256630_63680_00008_cd':'med_turbidity_cd'}, inplace = True)
temperature.rename(columns = {'149156_00010_00001':'max_temp', '149156_00010_00001_cd':'max_temp_cd','149157_00010_00002':'min_temp', '149157_00010_00002_cd':'min_temp_cd','149158_00010_00003':'mean_temp', '149158_00010_00003_cd':'mean_temp_cd'}, inplace = True)
gageheight.rename(columns = {'149155_00065_00003':'mean_gageheight', '149155_00065_00003_cd':'mean_gageheight_cd'}, inplace = True)
discharge.rename(columns = {'149154_00060_00003':'mean_discharge', '149154_00060_00003_cd':'mean_discharge_cd'}, inplace = True)

# writing easily readable versions of files to .csv files
turbidity.to_csv('turbidity.csv', na_rep=np.nan, header=True, index=False, sep=',')
temperature.to_csv('temperature.csv', na_rep=np.nan, header=True, index=False, sep=',')
gageheight.to_csv('gageheight.csv', na_rep=np.nan, header=True, index=False, sep=',')
discharge.to_csv('discharge.csv', na_rep=np.nan, header=True, index=False, sep=',')

# merging datasets. discharge has the longest record, so must be on left for every merge
d_gh = pd.merge(left=discharge, right=gageheight, how='left', left_on='datetime', right_on='datetime')
d_gh_tw = pd.merge(left=d_gh, right=temperature, how='left', left_on='datetime', right_on='datetime')
d_gh_tw_t = pd.merge(left=d_gh_tw, right=turbidity, how='left', left_on='datetime', right_on='datetime')

# writing combined file to csv
d_gh_tw_t.to_csv('all_data_12147600.csv', header=True,index=False,sep=',', na_rep=np.nan)
