import pandas as pd
import numpy as np
import datetime as dt
import os
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

bigtable = pd.read_csv('../tables/tolt_with_date_differences.csv')
justdis = pd.read_csv('../tables/minmaxval_table_flow.csv')
justwtemp = pd.read_csv('../tables/minmaxval_table_wtemp.csv')
justSWE = pd.read_csv('../tables/minmaxval_table_SWE.csv')

fig = plt.figure(figsize=(8, 4))
ax1 = fig.add_subplot(111)
for index, row in bigtable.iterrows():
    year = row['year']
    ax1.plot([year, year], [0, 365], 'k-.', linewidth=0.2)
    melt_start = row['SPsjul']
    melt_end = row['SPejul']
    p0 = ax1.plot([year, year], [melt_start, melt_end], 'k-', linewidth=0.5, label='spring melt')

p1 = ax1.scatter(bigtable.year, bigtable.SPsjul, marker='o', color='green',s=15, label='melt start date')
p2 = ax1.scatter(bigtable.year, bigtable.SPejul, marker='o', color='grey',s=15, label='melt end date')
p3 = ax1.scatter(bigtable.year, bigtable.min_flow_jul, marker='o', color='red',s=15, label='min flow date')
p4 = ax1.scatter(bigtable.year, bigtable.max_flow_jul, marker='o', color='blue',s=15, label='max flow date')

p5 = ax1.scatter(bigtable.year, bigtable.SPsjul, c=bigtable.max_swe, cmap='Greens', edgecolor='green',s=30, label='Max SWE [in]: min=%0.1f, max=%0.1f' % (bigtable['max_swe'].min(), bigtable['max_swe'].max()))
p6 = ax1.scatter(bigtable.year, bigtable.SPejul, c=bigtable.SWE_at_SP_melt, cmap='Greys', edgecolor='grey',s=30, label='SWE at melt onset [in]: min=%0.1f, max=%0.1f' % (bigtable['SWE_at_SP_melt'].min(), bigtable['SWE_at_SP_melt'].max()))
p7 = ax1.scatter(bigtable.year, bigtable.min_flow_jul, c=bigtable.min_discharge, cmap='Reds', edgecolor='red',s=30, label='Min discharge [ft^3/s]: min=%0.1f, max=%0.1f' % (bigtable['min_discharge'].min(), bigtable['min_discharge'].max()))
p8 = ax1.scatter(bigtable.year, bigtable.max_flow_jul,  c=bigtable.max_discharge, cmap='Blues', edgecolor='blue',s=30, label='Max discharge [ft^3/s]: min=%0.1f, max=%0.1f' % (bigtable['max_discharge'].min(), bigtable['max_discharge'].max()))

ax2 = ax1.twinx()
color = 'tab:black'
ax2.set_ylim([1, 13])
begs = np.arange(1,13,1)
begs = begs[::2]
ends = begs + 1
for i in range(len(begs)):
    plt.axhspan(begs[i], ends[i], alpha=0.05, color='gray')
ax2.set_ylabel('month')

ax1.set_title('timing of melt and low flow')
ax1.set_xlabel('water year (labeled with spring year)')
ax1.set_ylabel('julian day (days since Jan 1st)')
ax1.set_ylim([0, 365])
#ax1.legend(loc='best')
ax1.legend(handles=[p1, p2, p3, p4, p5, p6, p7, p8], bbox_to_anchor=(1.1, 1), loc='upper left')
fig.savefig('final_plots/melt_timing.png',format='png',
        bbox_inches='tight', pad_inches=0.5,dpi=300)
plt.close()


fig = plt.figure(figsize=(10, 10))
ax1 = fig.add_subplot(421)
ax1.axvspan(1996,2006, alpha=0.05, color='grey')
ax1.axvspan(2007,2018, alpha=0.05, color='red')
ax1.scatter(bigtable.year, bigtable.melt_period_days, marker='o', color='green',s=10, label='days of peak melt')
ax1.plot(bigtable.year, bigtable.melt_period_days, 'g--', linewidth=0.5)
ax1.set_ylabel('melt period length [days]')

ax1 = fig.add_subplot(422)
ax1.axvspan(1996,2006, alpha=0.05, color='grey')
ax1.axvspan(2007,2018, alpha=0.05, color='red')
ax1.scatter(bigtable.year, bigtable.max_swe, marker='o', color='green',s=10)
ax1.plot(bigtable.year, bigtable.max_swe, 'g--', linewidth=0.5)
ax1.set_ylabel('max SWE [in]')

ax1 = fig.add_subplot(423)
ax1.axvspan(1996,2006, alpha=0.05, color='grey')
ax1.axvspan(2007,2018, alpha=0.05, color='red')
ax1.scatter(bigtable.year, bigtable.peak_melt_rate, marker='o', color='green',s=10, label='n mid winter melt events')
ax1.plot(bigtable.year, bigtable.peak_melt_rate, 'g--', linewidth=0.5)
ax1.set_ylabel('melt rate [in SWE/day]')

ax1 = fig.add_subplot(424)
ax1.axvspan(1996,2006, alpha=0.05, color='grey')
ax1.axvspan(2007,2018, alpha=0.05, color='red')
ax1.scatter(bigtable.year, bigtable.n_mwme, marker='o', color='green',s=10, label='n mid winter melt events')
ax1.plot(bigtable.year, bigtable.n_mwme, 'g--', linewidth=0.5)
ax1.set_ylabel('n mid-winter melt events')

ax1 = fig.add_subplot(425)
ax1.axvspan(1996,2006, alpha=0.05, color='grey')
ax1.axvspan(2007,2018, alpha=0.05, color='red')
ax1.scatter(bigtable.year, bigtable.min_discharge, marker='o', color='green',s=10, label='days of peak melt')
ax1.plot(bigtable.year, bigtable.min_discharge, 'g--', linewidth=0.5)
ax1.set_ylabel('min discharge [ft^3/s]')

ax1 = fig.add_subplot(426)
ax1.axvspan(1996,2006, alpha=0.05, color='grey')
ax1.axvspan(2007,2018, alpha=0.05, color='red')
ax1.scatter(bigtable.year, bigtable.max_discharge, marker='o', color='green',s=10)
ax1.plot(bigtable.year, bigtable.max_discharge, 'g--', linewidth=0.5)
ax1.set_ylabel('max discharge [ft^3/s]')

ax1 = fig.add_subplot(427)
ax1.axvspan(1996,2006, alpha=0.05, color='grey')
ax1.axvspan(2007,2018, alpha=0.05, color='red')
ax1.scatter(bigtable.year, bigtable.min_flow_jul, marker='o', color='green',s=10, label='days of peak melt')
ax1.plot(bigtable.year, bigtable.min_flow_jul, 'g--', linewidth=0.5)
ax1.set_xlabel('year')
ax1.set_ylabel('doy min discharge')

ax1 = fig.add_subplot(428)
ax1.axvspan(1996,2006, alpha=0.05, color='grey')
ax1.axvspan(2007,2018, alpha=0.05, color='red')
ax1.scatter(bigtable.year, bigtable.max_flow_jul, marker='o', color='green',s=10)
ax1.set_xlabel('year')
ax1.plot(bigtable.year, bigtable.max_flow_jul, 'g--', linewidth=0.5)
ax1.set_ylabel('doy max discharge')

fig.savefig('final_plots/ztest_values.png',format='png',
        bbox_inches='tight', pad_inches=0.5,dpi=300)
plt.close()

fig = plt.figure(figsize=(4, 4))
ax1 = fig.add_subplot(111)
plt.yscale('log')
ax1.scatter(bigtable.max_swe, bigtable.min_discharge, marker='o', color='red',s=10, label='minimum')
ax1.scatter(bigtable.max_swe, bigtable.max_discharge, marker='o', color='blue',s=10, label='maximum')
ax1.set_title('discharge dependence on max SWE')
ax1.set_xlabel('maximum SWE [in]')
ax1.set_ylabel('discharge [ft^3/s]')
ax1.legend(loc='best')
fig.savefig('final_plots/discharge_vs_swe.png',format='png',
        bbox_inches='tight', pad_inches=0.5,dpi=300)
plt.close()

fig = plt.figure(figsize=(4, 4))
ax1 = fig.add_subplot(111)
plt.yscale('log')
ax1.scatter(bigtable.peak_melt_rate, bigtable.min_discharge, marker='o', color='red',s=10, label='minimum')
ax1.scatter(bigtable.peak_melt_rate, bigtable.max_discharge, marker='o', color='blue',s=10, label='maximum')
ax1.set_title('discharge dependence on peak melt rate')
ax1.set_xlabel('peak melt rate [in SWE/day]')
ax1.set_ylabel('discharge [ft^3/s]')
ax1.legend(loc='best')
fig.savefig('final_plots/discharge_vs_meltrate.png',format='png',
        bbox_inches='tight', pad_inches=0.5,dpi=300)
plt.close()

fig = plt.figure(figsize=(4, 4))
ax1 = fig.add_subplot(111)
plt.yscale('log')
ax1.scatter(bigtable.n_mwme, bigtable.min_discharge, marker='o', color='red',s=10, label='minimum')
ax1.scatter(bigtable.n_mwme, bigtable.max_discharge, marker='o', color='blue',s=10, label='maximum')
ax1.set_title('discharge dependence on MW melt events')
ax1.set_xlabel('n mid-winter-melt events')
ax1.set_ylabel('discharge [ft^3/s]')
ax1.legend(loc='best')
fig.savefig('final_plots/discharge_vs_mwme.png',format='png',
        bbox_inches='tight', pad_inches=0.5,dpi=300)
plt.close()
