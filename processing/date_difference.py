import pandas as pd
import numpy as np
import datetime as dt

# importing table
tolt_table = pd.read_csv('tolt_table.csv')

# converting values in date rows to to datetime types
tolt_table['min_discharge_date'] = tolt_table['min_discharge_date'].astype('datetime64[ns]')
tolt_table['max_discharge_date'] = tolt_table['max_discharge_date'].astype('datetime64[ns]')
tolt_table['zero_SWE_date'] = tolt_table['zero_SWE_date'].astype('datetime64[ns]')
tolt_table['max_SWE_date'] = tolt_table['max_SWE_date'].astype('datetime64[ns]')

# creating empty lists to fill with dates
datetimes_start_date = []
datetimes_end_date = []

# looping through table to convert str dates and years to datetime strings
for index, row in tolt_table.iterrows():

    year = row['year']
    SP_start = row['SP_melt_start_date']
    SP_end = row['SP_melt_end_date']
    [sday, smon] = SP_start.split('-')
    [eday, emon] = SP_end.split('-')

    if smon == 'Jan':
        smoni = 1
    if smon == 'Feb':
        smoni = 2
    if smon == 'Mar':
        smoni = 3
    if smon == 'Apr':
        smoni = 4
    if smon == 'May':
        smoni = 5
    if smon == 'Jun':
        smoni = 6
    if smon == 'Jul':
        smoni = 7

    if emon == 'Jan':
        emoni = 1
    if emon == 'Feb':
        emoni = 2
    if emon == 'Mar':
        emoni = 3
    if emon == 'Apr':
        emoni = 4
    if emon == 'May':
        emoni = 5
    if emon == 'Jun':
        emoni = 6
    if emon == 'Jul':
        emoni = 7

    # creating datetimes
    start_SP_date = dt.datetime(int(year),int(smoni),int(sday))
    end_SP_date = dt.datetime(int(year),int(emoni),int(eday))

    # adding datetimes to list
    datetimes_start_date.append(start_SP_date)
    datetimes_end_date.append(end_SP_date)

# adding lists of datetimes to tolt table
tolt_table['start_melt_date'] = datetimes_start_date
tolt_table['end_melt_date'] = datetimes_end_date

# creating empty lists to fill with day differences
peak_melting_days = []
melt_start_to_low_flow_days = []
melt_end_to_low_flow_days = []
SWE0_to_low_flow_days = []
SWEmax_to_low_flow_days = []
SPsjul = []
SPejul = []
SWE0jul = []
peak_swe_jul = []
min_flow_jul = []
max_flow_jul = []

# looping through table again to get date differences
for index,row in tolt_table.iterrows():
    SP_start_date = row['start_melt_date']
    SP_end_date = row['end_melt_date']
    SWE0_date = row['zero_SWE_date']
    peak_SWE_date = row['max_SWE_date']
    min_flow_date = row['min_discharge_date']
    max_flow_date = row['max_discharge_date']

    # calculating difference in days
    melt_period = SP_end_date - SP_start_date
    peak_melting_days.append(melt_period.days)
    
    melt_end_to_low = min_flow_date - SP_end_date
    melt_end_to_low_flow_days.append(melt_end_to_low.days)

    SWE0_to_low = min_flow_date - SWE0_date
    SWE0_to_low_flow_days.append(SWE0_to_low.days)

    # calculating time tuple for all of the dates
    SPstt = SP_start_date.timetuple()
    SPett = SP_end_date.timetuple()
    SWE0tt = SWE0_date.timetuple()
    peak_swe_tt = peak_SWE_date.timetuple()
    min_flow_tt = min_flow_date.timetuple()
    max_flow_tt = max_flow_date.timetuple()
    
    # appending doy from time tuple to lists for each date category
    SPsjul.append(SPstt.tm_yday)
    SPejul.append(SPett.tm_yday)
    SWE0jul.append(SWE0tt.tm_yday)
    peak_swe_jul.append(peak_swe_tt.tm_yday)
    min_flow_jul.append(min_flow_tt.tm_yday)
    max_flow_jul.append(max_flow_tt.tm_yday)

# adding date differences to dataframe
tolt_table['melt_period_days'] = peak_melting_days
tolt_table['melt_end_to_low_days'] = melt_end_to_low_flow_days
tolt_table['SWE0_to_low_flow_days'] = SWE0_to_low_flow_days

# calculating melted inches/day rate during peak melt
tolt_table['peak_melt_rate'] = tolt_table['SWE_at_SP_melt'].values / tolt_table['melt_period_days'].values

# adding julian days to dataframe
tolt_table['SPsjul'] = SPsjul
tolt_table['SPejul'] = SPejul
tolt_table['SWE0jul'] = SWE0jul
tolt_table['peak_swe_jul'] = peak_swe_jul
tolt_table['min_flow_jul'] = min_flow_jul
tolt_table['max_flow_jul'] = max_flow_jul

# writint table to new file
tolt_table.to_csv('tolt_with_date_differences.csv', header=True, index=False, na_rep=np.nan)
