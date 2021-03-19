import pandas as pd
import numpy as np
import argparse
import os
import matplotlib.pyplot as plt
from pyproj import Proj
from matplotlib.colors import Normalize
from scipy import ndimage
import datetime as dt

def main(args):

    # writing log file for reproducibility
    logfile = '%s_log.txt' % args.op[:-4]
    os.system("rm %s" % logfile)
    outF = open(logfile, 'w')
    outF.write('Input arguments to getminmax.py: ')
    outF.write('\n')
    outF.write('\n')
    print (args, file=outF)
    outF.close()
    
    # checking to see if we should use a logarithmic y scale
    plotlog = True
    if args.nl is not None:
        if args.nl == 'y':
            plotlog = False

    # checking see whether filtered quantities should be calculated
    p1dm = True
    p15dm = False
    p30dm = False
    if args.p15dm is not None:
        if args.p15dm == 'y':
            p15dm = True
    if args.p30dm is not None:
        if args.p30dm == 'y':
            p30dm = True

    # reading in file, converting datetime column to datetime type
    if args.infile_snotel is not None:
        dfstreams = pd.read_csv(args.infile_stream)
        dfsnowtel = pd.read_csv(args.infile_snotel)
        df1 = pd.merge(left=dfstreams, right=dfsnowtel, how='left', left_on='datetime', right_on='datetime')
    else:
        df1 = pd.read_csv(args.infile_stream)

    df1['datetime'] = df1['datetime'].astype('datetime64[ns]')
    df1['month'] = pd.DatetimeIndex(df1['datetime']).month
    df1['year'] = pd.DatetimeIndex(df1['datetime']).year
    df1['day'] = pd.DatetimeIndex(df1['datetime']).day
    df1['doy'] = pd.DatetimeIndex(df1['datetime']).dayofyear
    
    # trimming dataframe to only include bounding dates
    mindate = args.bounds[0]
    maxdate = args.bounds[1]

    minmonth = mindate[0:2]
    minday = mindate[3:5]
    minyear = mindate[6:10]

    maxmonth = maxdate[0:2]
    maxday = maxdate[3:5]
    maxyear = maxdate[6:10]

    years = np.arange(int(minyear), int(maxyear)+1, 1)

    minvals = []
    maxvals = []
    mindates = []
    maxdates = []
    filter = []

    fig = plt.figure(figsize=(6.5, 5))

    if plotlog:
        plt.yscale('log')

    for i in range(len(years)-1):
        mindatei = '%s-%s-%s' % (minmonth, minday, years[i])
        maxdatei = '%s-%s-%s' % (maxmonth, maxday, years[i+1])
        
        print (mindatei, maxdatei)
        
        df = df1[(df1.datetime >= mindatei) & (df1.datetime <= maxdatei)]
        
        try:
            minyear = df['year'].min()
            maxyear = df['year'].max()
            print (minyear, maxyear)

            # restricting range to search for min/max values to avoid values in adjacent water years
            dfmaxsearch = df[((df.month > 10) & (df.year == minyear)) | ((df.month < 9) & (df.year == maxyear))]
            dfminsearch = df[(df.month > 4) & (df.year == maxyear)]
            minval = dfminsearch[args.c1].min()
            maxval = dfmaxsearch[args.c1].max()

            minval_date = dfminsearch[dfminsearch[args.c1] == minval]['datetime'].values[0]
            maxval_date = dfmaxsearch[dfmaxsearch[args.c1] == maxval]['datetime'].values[0]
        except:
            print ('insufficient data for this year: ', mindatei,maxdatei)
            print ('Skipping .....')
            continue

        minvals.append(minval)
        maxvals.append(maxval)
        mindates.append(minval_date)
        maxdates.append(maxval_date)
        filter.append('1')

        # creating smoothed curve for entered parameter
        if p30dm:
            sigma = 30 # days
            gridsp = 1 # days
            npts = sigma/2/gridsp
            df['smooth_30'] = ndimage.filters.gaussian_filter(df[args.c1].values, npts)
            
            minval30 = df['smooth_30'].min()
            maxval30 = df['smooth_30'].max()
            minval_date30 = df[df['smooth_30'] == minval30]['datetime'].values[0]
            maxval_date30 = df[df['smooth_30'] == maxval30]['datetime'].values[0]
        
            minvals.append(minval30)
            maxvals.append(maxval30)
            mindates.append(minval_date30)
            maxdates.append(maxval_date30)
            filter.append('30')

        if p15dm:
            sigma = 15 # days
            gridsp = 1 # days
            npts = sigma/2/gridsp
            df['smooth_15'] = ndimage.filters.gaussian_filter(df[args.c1].values, npts)

            minval15 = df['smooth_15'].min()
            maxval15 = df['smooth_15'].max()
            minval_date15 = df[df['smooth_15'] == minval15]['datetime'].values[0]
            maxval_date15 = df[df['smooth_15'] == maxval15]['datetime'].values[0]

            minvals.append(minval15)
            maxvals.append(maxval15)
            mindates.append(minval_date15)
            maxdates.append(maxval_date15)
            filter.append('15')

        if plotlog:
            alphan = 0.05
        else:
            alphan = 0.5
        dosy = np.arange(0, len(df))
        df['day_of_snow_year'] = dosy
        if args.mm == '30d':
            if not p30dm:
                print ('must include flag "-p30dm y" to plot 30 day mean')
                print ('exiting ... ')
                exit()
            plt.plot(df.day_of_snow_year, df.smooth_30, color='gray',linewidth=3,alpha=alphan, label='yearly data')
        elif args.mm == '15d':
            if not p15dm:
                print ('must include flag "-p15dm y" to plot 15 day mean')
                print ('exiting ... ')
                exit()
            plt.plot(df.day_of_snow_year, df.smooth_15, color='gray',linewidth=3,alpha=alphan, label='yearly data')
        else:
            plt.plot(df.day_of_snow_year, df[args.c1], color='gray',linewidth=3,alpha=alphan, label='yearly data')

    # calculating statistics for each day in the year
    min_vals = []
    max_vals = []
    median_vals = []
    doys = []
    for doy in set(list(df1['doy'].values)):
        print (doy)
        df3 = df1[df1.doy == doy]
        median_val = df3[args.c1].median()
        min_val = df3[args.c1].min()
        max_val = df3[args.c1].max()
        median_vals.append(median_val)
        min_vals.append(min_val)
        max_vals.append(max_val)
        doys.append(doy)

    stats_df = pd.DataFrame({'doy':doys, 'min_vals':min_vals, 'max_vals':max_vals, 'median_vals':median_vals})

    # extracting a year we know has good/complete data
    mindatei = '%s-%s-%s' % (minmonth, minday, 2005)
    maxdatei = '%s-%s-%s' % (maxmonth, maxday, 2006)
    df = df1[(df1.datetime >= mindatei) & (df1.datetime <= maxdatei)]
    dosy = np.arange(0, len(df))
    df['day_of_snow_year'] = dosy

    min_dosys = []
    max_dosys = []
    med_dosys = []
    dosys = []
    doys = []
    for dosy in df['day_of_snow_year'].values:
        df2 = df[df.day_of_snow_year == dosy]
        doy = df2['doy'].values[0]
        stats2 = stats_df[stats_df.doy == doy]
        min_dosy = stats2['min_vals'].values[0]
        max_dosy = stats2['max_vals'].values[0]
        median_dosy = stats2['median_vals'].values[0]
        min_dosys.append(min_dosy)
        max_dosys.append(max_dosy)
        med_dosys.append(median_dosy)
        dosys.append(dosy)
        doys.append(doy)

    begmonths = df[df.day == 1]
    begs = begmonths['day_of_snow_year'].values
    begs = begs[::2]
    ends = begs + 30
    for i in range(len(begs)):
        plt.axvspan(begs[i], ends[i], alpha=0.05, color='gray')

    if args.plotlowyear is not None:
        if args.plotlowyear == 'y':
            # extracting a year we know had very low snow
            mindatei = '%s-%s-%s' % (minmonth, minday, 2014)
            maxdatei = '%s-%s-%s' % (maxmonth, maxday, 2015)
            df1415 = df1[(df1.datetime >= mindatei) & (df1.datetime <= maxdatei)]
            dosy = np.arange(0, len(df1415))
            df1415['day_of_snow_year'] = dosy
            plt.plot(dosy, df1415[args.c1].values, color='red', linewidth=2, alpha=0.2, label='2014-2015 snow year')
    if args.plothighyear is not None:
        if args.plothighyear == 'y':
            # extracting a year we know had very high snow
            mindatei = '%s-%s-%s' % (minmonth, minday, 2007)
            maxdatei = '%s-%s-%s' % (maxmonth, maxday, 2008)
            df0708 = df1[(df1.datetime >= mindatei) & (df1.datetime <= maxdatei)]
            dosy = np.arange(0, len(df0708))
            df0708['day_of_snow_year'] = dosy
            plt.plot(dosy, df0708[args.c1].values, color='blue', linewidth=2, alpha=0.2, label='2007-2008 snow year')
    if args.plotmedyear is not None:
        if args.plotmedyear == 'y':
            # extracting a year we know had very high snow
            mindatei = '%s-%s-%s' % (minmonth, minday, 2005)
            maxdatei = '%s-%s-%s' % (maxmonth, maxday, 2006)
            df0708 = df1[(df1.datetime >= mindatei) & (df1.datetime <= maxdatei)]
            dosy = np.arange(0, len(df0708))
            df0708['day_of_snow_year'] = dosy
            plt.plot(dosy, df0708[args.c1].values, color='yellow', linewidth=2, alpha=0.4, label='2005-2006 snow year')

    # trimming dataframe to only include bounding dates
    mindate = args.bounds[0]
    maxdate = args.bounds[1]
    minyear = int(mindate[6:10])
    maxyear = int(maxdate[6:10])

    minyear2, maxyear2 = int(df1['year'].min()), int(df1['year'].max())
    if maxyear2 < maxyear:
        maxyear = maxyear2
    if minyear2 > minyear:
        minyear = minyear2

    plt.title('All years %s - %s' % (minyear, maxyear))
    plt.xlabel('day of snow year')
    plt.ylabel('daily %s %s' % (args.c1, args.u1))
    plt.plot(dosys, med_dosys, color='black', linewidth=3, label='median')
    plt.legend(loc='best')
    fig.savefig('%s_all_years.png'%args.op[:-4],format='png',
            bbox_inches='tight', pad_inches=0.5,dpi=300)
    plt.close()
    
    
    # putting min max values in one dataframe
    minmaxs = pd.DataFrame({'minvals':minvals, 'maxvals':maxvals, 'mindates':mindates, 'maxdates':maxdates, 'filter':filter})
    print (minmaxs)
    
    if args.mm is not None:
        if args.mm == '30d':
            minmaxs = minmaxs[minmaxs['filter'] == '30']
        elif args.mm == '15d':
            minmaxs = minmaxs[minmaxs['filter'] == '15']
        else:
            minmaxs = minmaxs[minmaxs['filter'] == '1']
    else:
        minmaxs = minmaxs[minmaxs['filter'] == '1']

    # adding julian day values
    minjul = []
    maxjul = []
    yearmins = []
    yearmaxs = []
    for index,row in minmaxs.iterrows():
        mindate, maxdate = row['mindates'], row['maxdates']
        ttmin, ttmax = mindate.timetuple(), maxdate.timetuple()
        jmin = ttmin.tm_yday
        jmax = ttmax.tm_yday
        yearmin = ttmin.tm_year
        yearmax = ttmax.tm_year
        yearmins.append(yearmin)
        yearmaxs.append(yearmax)
        minjul.append(jmin)
        maxjul.append(jmax)
    
    print (len(minjul))
    print (len(minmaxs))
    minmaxs['minjul'] = minjul
    minmaxs['maxjul'] = maxjul
    minmaxs['yearmin'] = yearmins
    minmaxs['yearmax'] = yearmaxs

    minmaxs['minmonth'] = pd.DatetimeIndex(minmaxs['mindates']).month
    minmaxs['maxmonth'] = pd.DatetimeIndex(minmaxs['maxdates']).month
    minmaxs['minyear'] = pd.DatetimeIndex(minmaxs['mindates']).year
    minmaxs['maxyear'] = pd.DatetimeIndex(minmaxs['maxdates']).year
    minmaxs['minday'] = pd.DatetimeIndex(minmaxs['mindates']).day
    minmaxs['maxday'] = pd.DatetimeIndex(minmaxs['maxdates']).day
    
    print (minmaxs.info())
    print (minmaxs.mindates)
    print (minmaxs.minvals)

    fig = plt.figure(figsize=(8, 4))
    ax1 = fig.add_subplot(111)

    if plotlog:
        plt.yscale('log')
    
    ax1.plot_date(x=minmaxs.mindates, y=minmaxs.minvals, marker='o', color='red', label='minimums')
    ax1.plot_date(x=minmaxs.maxdates, y=minmaxs.maxvals, marker='o', color='blue', label='maximums')
    
    ax1.set_xlabel('date')
    ax1.set_ylabel('daily %s %s' % (args.c1, args.u1))
    ax1.legend(loc='best')
    fig.savefig(args.op,format='png',
            bbox_inches='tight', pad_inches=0.5,dpi=300)
    plt.close()

    fig = plt.figure(figsize=(8, 6))
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    if plotlog:
        plt.yscale('log')


    fig = plt.figure(figsize=(8, 4))
    ax1 = fig.add_subplot(111)
    if plotlog:
        plt.yscale('log')

    ax1.scatter(minmaxs.minjul, minmaxs.minvals, marker='o', color='red',s=25, label='minimums')
    ax1.scatter(minmaxs.maxjul, minmaxs.maxvals, marker='o', color='blue',s=25, label='maximums')
    con = ax1.scatter(minmaxs.maxjul, minmaxs.maxvals, c=minmaxs.yearmax,s=15,edgecolors='none',cmap='Greys')
    ax1.scatter(minmaxs.minjul, minmaxs.minvals, c=minmaxs.yearmin,s=15,edgecolors='none',cmap='Greys')

    cbar = fig.colorbar(con)
    cbar.set_label('year')
    ax1.set_xlabel('julian day (days since Jan 1st)')
    ax1.set_ylabel('daily %s %s' % (args.c1, args.u1))
    ax1.set_xlim([0, 365])
    ax1.legend(loc='best')
    fig.savefig('%s_juliandays.png'%args.op[:-4],format='png',
            bbox_inches='tight', pad_inches=0.5,dpi=300)
    plt.close()

    fig = plt.figure(figsize=(8, 4))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    #plt.yscale('log')

    ax1.scatter(minmaxs.minyear, minmaxs.minvals, marker='o', color='red',s=25, label='minimums')
    ax2.scatter(minmaxs.maxyear, minmaxs.maxvals, marker='o', color='blue',s=25, label='maximums')
    ax1.set_title('yearly minimum values')
    ax2.set_title('yearly maximum values')
    ax1.set_xlabel('year')
    ax2.set_xlabel('year')
    ax1.set_ylabel('daily %s %s' % (args.c1, args.u1))
    #ax2.set_ylabel('daily %s %s' % (args.c1, args.u1))
    fig.savefig('%s_by_year.png'%args.op[:-4],format='png',
            bbox_inches='tight', pad_inches=0.5,dpi=300)
    plt.close()

    fig = plt.figure(figsize=(8, 4))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    #plt.yscale('log')

    ax1.scatter(minmaxs.minyear, minmaxs.minjul, marker='o', color='red',s=25, label='minimums')
    ax2.scatter(minmaxs.maxyear, minmaxs.maxjul, marker='o', color='blue',s=25, label='maximums')
    ax1.set_title('julian day of minimum')
    ax2.set_title('julian day of maximum')
    ax1.set_xlabel('year')
    ax2.set_xlabel('year')
    ax1.set_ylabel('julian day (days since Jan 1st)')
    ax1.set_ylim([0, 360])
    ax2.set_ylim([0, 360])
    #ax2.set_ylabel('daily %s %s' % (args.c1, args.u1))
    fig.savefig('%s_JD_x_year.png'%args.op[:-4],format='png',
            bbox_inches='tight', pad_inches=0.5,dpi=300)
    plt.close()
        
# Help/description and command line argument parser
if __name__=='__main__':
    desc = '''

        '''
    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument('-op', '--op', dest='op', type=str, required=True,
                        help='file to plot data to e.g.: "tolt_08.01.2016-08.01.2017.png"')
    parser.add_argument('-infile_stream', '--infile_stream', dest='infile_stream', type=str, required=True,
                        help='infile_stream: file to read stream data from')
    parser.add_argument('-infile_snotel', '--infile_snotel', dest='infile_snotel', type=str, required=False,
                        help='infile_snotel: file to read snotel data from')
    parser.add_argument('-p1dm', '--p1dm', dest='p1dm', type=str, required=False,
                        help='p1dm: plot 1 day mean')
    parser.add_argument('-p15dm', '--p15dm', dest='p15dm', type=str, required=False,
                        help='p30dm: plot 15 day mean')
    parser.add_argument('-p30dm', '--p30dm', dest='p30dm', type=str, required=False,
                        help='p1dm: plot 30 day mean')
                        
    parser.add_argument('-plotlowyear', '--plotlowyear', dest='plotlowyear', type=str, required=False,
                        help='enter "-plotlowyear y" to include 2014-2015 snow year in red on plot')
    parser.add_argument('-plothighyear', '--plothighyear', dest='plothighyear', type=str, required=False,
                        help='enter "-plothighyear y" to include 2007-2008 snow year in blue on plot')
    parser.add_argument('-plotmedyear', '--plotmedyear', dest='plotmedyear', type=str, required=False,
                        help='enter "-plotmedyear y" to include 2005-2006 snow year in yellow on plot')

    parser.add_argument('-b', '--bounds', metavar=('mindate', 'maxdate'), required=True,
                        dest='bounds', type=str, nargs=2,
                        help='date bounds e.g. [1987-09-08, 1988-09-08]')
    parser.add_argument('-c1', '--c1', dest='c1', type=str, required=True,
                        help='c1: first column to plot (e.g. "-c2 min_temp")')
    parser.add_argument('-u1', '--u1', dest='u1', type=str, required=True,
                        help='c1: first column to plot (e.g. "-u2 [degC]")')
    parser.add_argument('-nl', '--nl', dest='nl', type=str, required=False,
                        help='nl: flag "-nl y" to not plot value in log scale on the y axis. Default is to plot y axis on the log scale.')
    parser.add_argument('-mm', '--mm', dest='mm', type=str, required=False,
                        help='mm: flag indicating which smoothing to plot min/max values for. Default is no smoothing. enter "-mm 30d" to plot 30 day mean or "-mm 15d" to plot 15 day mean')


    pargs = parser.parse_args()
    
    #cProfile.run('main(pargs)')
    main(pargs)
