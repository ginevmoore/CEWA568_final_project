import pandas as pd
import numpy as np

skookum = pd.read_csv('bcqc_47.68000_-121.61000.txt', delim_whitespace=True, names = ['year','month','day','daily_precip_in','max_air_temp_F','min_air_temp_F','mean_air_temp_F','SWE_in'])

datetimes = []
for i, r in skookum.iterrows():
    y, m, d = r['year'], r['month'], r['day']
    if m < 10:
        m = '0%i' % m
    else:
        m = '%i' % m
    if d < 10:
        d = '0%i' % d
    else:
        d = '%i' % d
    datetime = '%i-%s-%s' % (y,m,d)
    datetimes.append(datetime)

skookum['datetime'] = datetimes

skookum.to_csv('skookum_snotel.csv',header=True,index=False,na_rep=np.nan)
