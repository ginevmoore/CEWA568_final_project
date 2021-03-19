import os
import numpy as np

dates = np.arange(1960, 2021, 1)

for i in range(len(dates)-1):
    startyear = str(int(dates[i]))
    endyear = str(int(dates[i+1]))
    os.system("python plotyear.py -infile_stream /Users/ginevramoore/Desktop/CEWA568/final_project/data/all_data_12147600.csv -op water_years/12147600_09.01.%s-12.01.%s_temp.png -b 09.01.%s 12.01.%s -p1dm y -p15dm y -p30dm y -c1 mean_temp -u1 [degC] -mm 1d -nl y" % (startyear, endyear, startyear, endyear))

for i in range(len(dates)-1):
    startyear = str(int(dates[i]))
    endyear = str(int(dates[i+1]))
    os.system("python plotyear.py -infile_stream /Users/ginevramoore/Desktop/CEWA568/final_project/data/all_data_12147600.csv -op water_years/12147600_09.01.%s-12.01.%s.png -b 09.01.%s 12.01.%s -p1dm y -p15dm y -p30dm y -c1 mean_discharge -u1 [ft^3/m] -mm 1d" % (startyear, endyear, startyear, endyear))

for i in range(len(dates)-1):
    startyear = str(int(dates[i]))
    endyear = str(int(dates[i+1]))
    os.system("python plotyear.py -infile_stream ../data/all_data_12147600.csv -infile_snotel ../data/skookum_snotel.csv -nl y -b 09.01.%s 12.01.%s -c1 SWE_in -u1 [inches] -op water_years/09.01.%s-12.01.%s_SWE.png -p1dm y" % (startyear, endyear, startyear, endyear))
