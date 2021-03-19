import pandas as pd
import numpy as np
import argparse
import os
import matplotlib.pyplot as plt
from pyproj import Proj
from matplotlib.colors import Normalize
from scipy import ndimage

def main(args):

    # writing log file for reproducibility
    logfile = '%s_log.txt' % args.op[:-4]
    os.system("rm %s" % logfile)
    outF = open(logfile, 'w')
    outF.write('Input arguments to plotyear.py: ')
    outF.write('\n')
    outF.write('\n')
    print (args, file=outF)
    outF.close()

    # checking to make sure one mean is flagged to be plotted from input arguments
    p1dm = False
    p15dm = False
    p30dm = False
    if args.p1dm is not None:
        if args.p1dm == 'y':
            p1dm = True
    if args.p15dm is not None:
        if args.p15dm == 'y':
            p15dm = True
    if args.p30dm is not None:
        if args.p30dm == 'y':
            p30dm = True
    if not p1dm and not p15dm and not p30dm:
        print ('must enter "-p1dm y" and/or "-p15dm y" and/or "-p30dm y"')
        print ('exiting ..... ')
        exit()
        
    # reading in file, converting datetime column to datetime type
    if args.infile_snotel is not None:
        dfstreams = pd.read_csv(args.infile_stream)
        dfsnowtel = pd.read_csv(args.infile_snotel)
        df = pd.merge(left=dfstreams, right=dfsnowtel, how='left', left_on='datetime', right_on='datetime')
    else:
        df = pd.read_csv(args.infile_stream)

    df['datetime'] = df['datetime'].astype('datetime64[ns]')
    df['month'] = pd.DatetimeIndex(df['datetime']).month
    df['year'] = pd.DatetimeIndex(df['datetime']).year
    df['day'] = pd.DatetimeIndex(df['datetime']).day
    
    # trimming dataframe to only include bounding dates
    mindate = args.bounds[0]
    maxdate = args.bounds[1]
    df = df[(df.datetime >= mindate) & (df.datetime <= maxdate)]

    minyear = df['year'].min()
    maxyear = df['year'].max()
    #print (minyear, maxyear)

    # restricting range to search for min/max values to avoid values in adjacent water years
    if 'temp' not in args.c1:
        dfmaxsearch = df[((df.month > 10) & (df.year == minyear)) | ((df.month < 9) & (df.year == maxyear))]
        dfminsearch = df[(df.month > 4) & (df.year == maxyear)]
        minval = dfminsearch[args.c1].min()
        maxval = dfmaxsearch[args.c1].max()
    else:
        dfminsearch = df[((df.month > 10) & (df.year == minyear)) | ((df.month < 9) & (df.year == maxyear))]
        dfmaxsearch = df[(df.month > 4) & (df.year == maxyear)]
        minval = dfminsearch[args.c1].min()
        maxval = dfmaxsearch[args.c1].max()

    minval_date = dfminsearch[dfminsearch[args.c1] == minval]['datetime'].values[0]
    maxval_date = dfmaxsearch[dfmaxsearch[args.c1] == maxval]['datetime'].values[0]
    
    # creating smoothed curve for entered parameter
    if p30dm:
        sigma = 30 # days
        gridsp = 1 # days
        npts = sigma/2/gridsp
        df['smooth_30'] = ndimage.filters.gaussian_filter(df[args.c1].values, npts)
        if args.c2 is not None:
            df['smooth_30_2'] = ndimage.filters.gaussian_filter(df[args.c2].values, npts)
        
        dfmaxsearch = df[((df.month > 10) & (df.year == minyear)) | ((df.month < 9) & (df.year == maxyear))]
        dfminsearch = df[(df.month > 4) & (df.year == maxyear)]
        minval_30 = dfminsearch['smooth_30'].min()
        maxval_30 = dfmaxsearch['smooth_30'].max()

        minval_date_30 = dfminsearch[dfminsearch['smooth_30'] == minval_30]['datetime'].values[0]
        maxval_date_30 = dfmaxsearch[dfmaxsearch['smooth_30'] == maxval_30]['datetime'].values[0]

    if p15dm:
        sigma = 15 # days
        gridsp = 1 # days
        npts = sigma/2/gridsp
        df['smooth_15'] = ndimage.filters.gaussian_filter(df[args.c1].values, npts)
        if args.c2 is not None:
            df['smooth_15'] = ndimage.filters.gaussian_filter(df[args.c2].values, npts)

        dfmaxsearch = df[((df.month > 10) & (df.year == minyear)) | ((df.month < 9) & (df.year == maxyear))]
        dfminsearch = df[(df.month > 4) & (df.year == maxyear)]
        minval_15 = dfminsearch['smooth_15'].min()
        maxval_15 = dfmaxsearch['smooth_15'].max()

        minval_date_15 = dfminsearch[dfminsearch['smooth_15'] == minval_15]['datetime'].values[0]
        maxval_date_15 = dfmaxsearch[dfmaxsearch['smooth_15'] == maxval_15]['datetime'].values[0]

    # plotting discharge plot for the specified date range
    fig = plt.figure(figsize=(8, 4))
    ax1 = fig.add_subplot(111)
    plotlog = True
    if args.nl is not None:
        if args.nl == 'y':
            plotlog = False

    if plotlog:
        plt.yscale('log')

    if args.c2 is not None:
        ax2 = ax1.twinx()
        color = 'tab:green'
    if p1dm:
        ax1.plot(df['datetime'].values, df[args.c1].values, 'k-', label='daily mean %s' % args.c1, linewidth=1, alpha=0.7)
        if args.c2 is not None:
            ax2.plot(df['datetime'].values, df[args.c2].values, 'k-.', linewidth=1, label='daily mean %s' % args.c2)
    if p30dm:
        ax1.plot(df['datetime'].values, df['smooth_30'].values, 'b-',  linewidth=1, alpha=0.7, label='30-day mean')
        if args.c2 is not None:
            ax2.plot(df['datetime'].values, df['smooth_30_2'].values, 'b-.', linewidth=1)
    if p15dm:
        ax1.plot(df['datetime'].values, df['smooth_15'].values, 'r-', linewidth=1, alpha=0.7, label='15-day mean')
        if args.c2 is not None:
            ax2.plot(df['datetime'].values, df['smooth_15_2'].values, 'r-.', linewidth=1)

    if 'discharge' in args.c1:
        minplot, maxplot = 1e0, 1e4
    elif 'SWE' in args.c1:
        minplot, maxplot = 0, 100
    else:
        minplot, maxplot = 0, maxval+maxval/4

    minval_plot, minval_date_plot = minval, minval_date
    maxval_plot, maxval_date_plot = maxval, maxval_date
    if args.mm is not None:
        if args.mm == '30d':
            minval_plot, minval_date_plot = minval_30, minval_date_30
            maxval_plot, maxval_date_plot = maxval_30, maxval_date_30
        if args.mm == '15d':
            minval_plot, minval_date_plot = minval_15, minval_date_15
            maxval_plot, maxval_date_plot = maxval_15, maxval_date_15

    ax1.plot([minval_date_plot, minval_date_plot], [minplot, maxplot], 'k-', linewidth=0.5)
    ax1.plot([maxval_date_plot, maxval_date_plot], [minplot, maxplot], 'k-', linewidth=0.5)
    ax1.scatter([minval_date_plot, maxval_date_plot], [minval_plot, maxval_plot])
    ax1.set_xlabel('date')
    ax1.set_ylabel('daily %s %s' % (args.c1, args.u1))
    ax1.legend(loc='best')
    ax1.set_xlim([mindate, maxdate])
    ax1.set_ylim([minplot, maxplot])
    #ax1.grid()

    if args.c2 is not None:
        ax2.set_ylabel('daily %s %s' % (args.c2, args.u2))
        ax2.legend(loc='best')
        #ax2.grid()

    fig.savefig(args.op,format='png',
            bbox_inches='tight', pad_inches=0.5,dpi=300)
    plt.close()

    print (maxyear,',',minval_date_plot,',',minval_plot,',',maxval_date_plot,',',maxval_plot)


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
    parser.add_argument('-b', '--bounds', metavar=('mindate', 'maxdate'), required=True,
                        dest='bounds', type=str, nargs=2,
                        help='date bounds e.g. [1987-09-08, 1988-09-08]')
    parser.add_argument('-c1', '--c1', dest='c1', type=str, required=True,
                        help='c1: first column to plot (e.g. "-c2 min_temp")')
    parser.add_argument('-u1', '--u1', dest='u1', type=str, required=True,
                        help='c1: first column to plot (e.g. "-u2 [degC]")')
    parser.add_argument('-c2', '--c2', dest='c2', type=str, required=False,
                        help='c1: first column to plot (e.g. "-c2 mean_discharge")')
    parser.add_argument('-u2', '--u2', dest='u2', type=str, required=False,
                        help='u2: first column to plot (e.g. "-u2 [ft^3/m]")')
    parser.add_argument('-nl', '--nl', dest='nl', type=str, required=False,
                        help='nl: flag "-nl y" to not plot value in log scale on the y axis. Default is to plot y axis on the log scale.')
    parser.add_argument('-mm', '--mm', dest='mm', type=str, required=False,
                        help='mm: flag indicating which smoothing to plot min/max values for. Default is no smoothing. enter "-mm 30d" to plot 30 day mean or "-mm 15d" to plot 15 day mean')

    pargs = parser.parse_args()
    
    #cProfile.run('main(pargs)')
    main(pargs)
