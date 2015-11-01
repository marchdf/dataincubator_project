#!/usr/bin/env python

#==============================================================
# Parse data from WunderGround and answer the following:
#
# What is the average monthly temperature in AA over the last several
# years?
#
# How is it related to our utility bill and gas usage?
#
#==============================================================
__author__ = 'marchdf'
def usage():
    print '\nUsage: {0:s} [options ...]\nOptions:\n -f, --force\tforce redownload data\n -h, --help\tshow this message and exit\n'.format(sys.argv[0])


#================================================================================
#
# Imports
#
#================================================================================
import sys,getopt
import time
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import urllib2
import shutil
import csv
import numpy as np
from subprocess import call
import matplotlib.axis as axis
import pylab as pl
import os.path
from scipy.stats.stats import pearsonr
import calendar
                                                                                                                                                                                      
#================================================================================
#
# Parse arguments
#
#================================================================================
redownload = False
try:
    myopts, args = getopt.getopt(sys.argv[1:],"hf",["help","force"])
except getopt.GetoptError as e:
    print (str(e))
    usage()
    sys.exit(2)

for o, a in myopts:               
    if o in ('-h', '--help'):
        usage()
        sys.exit()
    elif o in ('-f', '--force'):
        redownload = True 

#================================================================================
#
# Some defaults variables
#
#================================================================================
pl.rc('text', usetex=True)
pl.rc('font', family='serif', serif='Times')
pl.matplotlib.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
cmap_med =['#F15A60','#7AC36A','#5A9BD4','#FAA75B','#9E67AB','#CE7058','#D77FB4','#737373']
cmap =['#EE2E2F','#008C48','#185AA9','#F47D23','#662C91','#A21D21','#B43894','#010202']
dashseq = [(None,None),[10,5],[10, 4, 3, 4],[3, 3],[10, 4, 3, 4, 3, 4],[3, 3],[3, 3]];
markertype = ['s','d','o','p','h']


#================================================================================
#
# Define some functions
#
#================================================================================

def parse_data(fname):
    # Read data from csv file and output it to two vectors
    # one is the date of the data
    # the other is the temperature

    f = open(fname, 'rt')
    format = '%Y-%m-%d'
    dates = []
    max_temp = []
    avg_temp = []
    min_temp = []

    try:
        reader = csv.reader(f)
        reader.next() # skip first line
        reader.next() # skip second line
        for cnt, row in enumerate(reader):

            dates.append(datetime.strptime(row[0], format))
            max_temp.append(row[1])
            avg_temp.append(row[2])
            min_temp.append(row[3])

    finally:
        f.close()

    return dates,min_temp,avg_temp,max_temp


def bin_data(dates,temp):
    # Bin the data from parse_data into the respective months of the
    # year. Returns the avg monthly temperature and the associated
    # months in that year in datetime format

    # Initialize vectors
    dt_months         = [] # months of year in dt format
    months            = np.arange(1,13)
    monthly_temp      = np.zeros(len(months))
    num_days_in_month = np.zeros(len(months))

    # Get the number of days in each month for this year
    this_year = dates[1].year
    for cnt,month in enumerate(months):
        num_days_in_month[cnt] = calendar.monthrange(this_year,month)[1]
        dt_months.append(datetime.strptime(str(this_year)+'-'+str(month), '%Y-%m'))

    # Loop over each date to get the daily temperature
    for cnt,dt in enumerate(dates):
        idx = dt.month - 1 # -1 bc months start at 1 (Jan.)
        monthly_temp[idx] += float(temp[cnt])

    # Average the temperature
    avg_monthly_temp = monthly_temp/num_days_in_month

    return dt_months,avg_monthly_temp

def get_hdd(dates,min_temp,max_temp):
    # Get the number of Heating Degree Days

    # Base temperature for HDD calculation
    base_temp = 65.0

    # Initialize vectors
    dt_months         = [] # months of year in dt format
    months            = np.arange(1,13)
    monthly_hdd       = np.zeros(len(months))
    num_days_in_month = np.zeros(len(months))

    # Get the number of days in each month for this year
    this_year = dates[1].year
    for cnt,month in enumerate(months):
        num_days_in_month[cnt] = calendar.monthrange(this_year,month)[1]
        dt_months.append(datetime.strptime(str(this_year)+'-'+str(month), '%Y-%m'))

    # Loop over each date to get the daily hdd
    for cnt,dt in enumerate(dates):
        idx = dt.month - 1 # -1 bc months start at 1 (Jan.)
        monthly_hdd[idx] += calc_hdd(base_temp,float(min_temp[cnt]),float(max_temp[cnt]))

    # Average the HDD in each month
    avg_monthly_hdd = monthly_hdd/num_days_in_month

    return dt_months,monthly_hdd,avg_monthly_hdd


def calc_hdd(base_temp,min_temp,max_temp): 
    # Calc HDD based on the following formula
    # if (Tmin+Tmax)/2 > Tbase: HDD = 0
    # else                      HDD = Tbase - (Tmin+Tmax)/2
    hdd_temp = 0.5*(min_temp + max_temp)
    if hdd_temp > base_temp:
        return 0
    else:
        return base_temp - hdd_temp


def download_file(fname,dt_start,dt_end):

    # Setup url    
    baseurl = 'http://www.wunderground.com/history/airport/KARB/'
    sdate_start = dt_start.strftime("%Y/%m/%d") #'2012/9/1'
    sdate_end = '/CustomHistory.html?dayend='+dt_end.strftime("%d")+'&monthend='+dt_end.strftime("%m")+'&yearend='+dt_end.strftime("%Y")
    suffix = '&req_city=NA&req_state=NA&req_statename=NA&format=1'
    page = baseurl+sdate_start+sdate_end+suffix

    # Get the data from the website
    print '       getting data from this page: ',page
    response = urllib2.urlopen(page)
    
    # Save it to a file
    with open(fname, 'wb') as fp:
        shutil.copyfileobj(response, fp)

def parse_money_data(fname):
    f = open(fname, 'rt')
    format = '%Y-%m'
    dates = []
    utilities = []
    gas_rates = []

    try:
        reader = csv.reader(f)
        # skip comments line
        reader.next()
        for cnt, row in enumerate(reader):
            dates.append(datetime.strptime(row[0], format))
            utilities.append(row[1])
            gas_rates.append(row[2])

    finally:
        f.close()
        
    
    # convert to float
    utilities = np.array([ float(x) for x in utilities])
    gas_rates = np.array([ float(x) for x in gas_rates])


    return dates, utilities, gas_rates

def plot_year_color_code(year_start,year_end,dates,y):
    # plot data and color code by the year

    # loop over the years
    for k, year in enumerate(range(year_start,year_end+1)):

        # get the subset corresponding to the year (to color code)
        mo = [x for x in dates if x.year == year]
        Y  = [y[cnt] for cnt, x in enumerate(dates) if x.year == year]
    
        # plot
        p = pl.plot(mo,Y,lw=3,color=cmap[k],marker='o',ms=8,mfc=cmap[k],mec=cmap[k]); p[0].set_dashes(dashseq[0]); 


def x_y_scatter(x,y,months,add_fit=None):
    # Scatter plot of monthly x vs y with an optional linear fit
    # (default to none, call with True to add a linear fit) Color code
    # the results by tenant year

    # loop over the years
    num_tenant_years = pl.shape(x)[0]
    for k in range(0,num_tenant_years):

        X  = x[k,:]
        Y  = y[k,:]
        mo = months[k]

        # loop on each month
        for cnt, m in enumerate(mo):
            
            # plot the main marker
            p = pl.plot(X[cnt],Y[cnt],marker=markertype[k],ms=20,mfc=cmap_med[k],mec='white',ls='none',alpha=0.7);

            # labe the marker by the month
            pl.text(X[cnt],Y[cnt],str(m.month),ha='center',va='center',fontsize=12,fontweight='bold',color=cmap[k])

        # Make a linear fit of the data and ignore zeros in Y (because
        # there is no data for those Y yet)
        if add_fit:
            idx = np.nonzero(Y)
            X = X[idx]
            Y = Y[idx]
            print X, Y
            fit = np.polyfit(X,Y,1)
            fit_fn = np.poly1d(fit)
            xx = np.linspace(X.min(),X.max(),100)
            p = pl.plot(xx,fit_fn(xx),ls='-',lw=2,color=cmap[k])
            p[0].set_dashes(dashseq[k]); 
        



def default_formats_figures(fignum):
    # Iterate over all figures and apply default formating
    for fig in np.arange(0,fignum):
        pl.figure(fig)
        pl.xlabel(r"months",fontsize=22,fontweight='bold')
        #pl.setp(pl.gca().get_xmajorticklabels(),fontsize=18,fontweight='bold');
        #pl.setp(pl.gca().get_ymajorticklabels(),fontsize=18,fontweight='bold');
        # pl.setp(pl.gca(),xlim=[0,24])
        # pl.gca().set_xticks(np.arange(0,24,6))
        # pl.gca().set_yticks(np.arange(0,7,2))
        pl.gca().spines['right'].set_color('none')
        pl.gca().spines['top'].set_color('none')
        pl.gca().xaxis.set_ticks_position('bottom')
        pl.gca().yaxis.set_ticks_position('left')
        # gcf().subplots_adjust(right=0.85)

def save_figures(fignames):
    # Save all the figures in different formats
    for cnt,figname in enumerate(fignames):
        pl.figure(cnt)
        pl.savefig(plotdir+figname+'.pdf',format='pdf')
        pl.savefig(plotdir+figname+'.png',format='png')
        #pl.savefig(plotdir+figname+'.eps',format='eps')


#================================================================================
#
# Basic information/setup
#
#================================================================================

# default directory to save data (create it if necessary)
datadir = './daily_avg/'
if not os.path.exists(datadir):
    os.makedirs(datadir)

# directory to save plots
plotdir = './plots/'
if not os.path.exists(plotdir):
    os.makedirs(plotdir)
    
# Setup the dates
today = datetime.today()
dt_end = today;
dt_start = datetime.strptime('2012/01/01', '%Y/%m/%d')
year_end = dt_end.year
year_start = dt_start.year
delta_years = relativedelta(dt_end, dt_start).years
month_labels = ['Sep','Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug']

#================================================================================
#
# Grab/parse the weather data
#
#================================================================================

# initialize the data
date = dt_start
all_avg_monthly_temp = np.zeros((delta_years+1)*12)
all_min_monthly_temp = np.zeros((delta_years+1)*12)
all_max_monthly_temp = np.zeros((delta_years+1)*12)
monthly_hdd          = np.zeros((delta_years+1)*12)
monthly_hdd_avg      = np.zeros((delta_years+1)*12)

all_months           = []

# loop over all the years
for k in range(0,delta_years+1):
    print 'Getting year worth of daily data starting on '+date.strftime("%Y/%m/%d")

    # file name to save
    fname= datadir+'data_'+date.strftime("%Y-%m-%d")+'.csv'

    # download the data
    if redownload:
        print "Forcing redownload of data file." 
        download_file(fname,date,date+relativedelta(years=1)-timedelta(days=1))
    else:
        try:
            with open(fname) as file:
                print 'Data file exists already. Using that.'
                pass
        except IOError as e:
            print "Data file does not exist yet."
            download_file(fname,date,date+relativedelta(years=1)-timedelta(days=1))

    # Parse the downloaded file
    raw_dates, raw_min_temp, raw_avg_temp, raw_max_temp = parse_data(fname)

    # Get the average monthly temperatures and store them
    dt_months,all_avg_monthly_temp[k*12:k*12+12] = bin_data(raw_dates,raw_avg_temp)
    _,all_min_monthly_temp[k*12:k*12+12]         = bin_data(raw_dates,raw_min_temp)
    _,all_max_monthly_temp[k*12:k*12+12]         = bin_data(raw_dates,raw_max_temp)
    all_months.extend(dt_months)

    # Get the Heating Degree Days
    _,monthly_hdd[k*12:k*12+12],monthly_hdd_avg[k*12:k*12+12] = get_hdd(raw_dates,raw_min_temp,raw_max_temp)

    # increment the date
    date += relativedelta(years=1)


#================================================================================
#
# Parse the utility bills and gas rates
#
#================================================================================
fname = 'utilities.csv'
utility_months, utilities, gas_rates = parse_money_data(fname)

# get the ccf used
ccf = utilities/gas_rates

# Get the temp and hdd subset corresponding to the utility data
avg_temp_subset = np.zeros(len(utility_months))
hdd_subset = np.zeros(len(utility_months))
for cnt, dt in enumerate(utility_months):
    avg_temp_subset[cnt] = all_avg_monthly_temp[all_months.index(dt)]
    hdd_subset[cnt]      = monthly_hdd[all_months.index(dt)]

#================================================================================
#
# Sort the data into tenant years (sept-aug)
#
#================================================================================
tenant_years = delta_years + 1
sorted_months = []
sorted_avg_temp   = np.zeros([tenant_years,12])
sorted_ccf        = np.zeros([tenant_years,12])
sorted_hdd        = np.zeros([tenant_years,12])

# loop on all the years
for k, year in enumerate(range(year_start,year_end+1)):

    # temporally store the months in a given tenant year
    tmp_months = []
    storing_cnt = 0

    # lower and upper date bounds (sept,year -> aug, year+1)
    dt_lbnd = datetime.strptime(str(year)+'-9',format('%Y-%m'))
    dt_ubnd = datetime.strptime(str(year+1)+'-8',format('%Y-%m'))

    # loop on all the utility months
    for cnt, mo in enumerate(utility_months):
        
        # if the month belongs to that tenant year, store it
        if  dt_lbnd <= mo and mo <= dt_ubnd:
            tmp_months.append(mo)
            sorted_ccf[k,storing_cnt]      = ccf[cnt]
            sorted_avg_temp[k,storing_cnt] = avg_temp_subset[cnt]
            sorted_hdd[k,storing_cnt]      = hdd_subset[cnt]
            storing_cnt += 1

    # append to the sorted months
    sorted_months.append(sorted(tmp_months))

    
# Get the ccf per degree Kelvin
sorted_K = (sorted_avg_temp-32)/1.8 + 273.15
ccf_per_temp = sorted_ccf/sorted_K

# Get the ccf per hdd
ccf_per_hdd  = sorted_ccf/sorted_hdd


#================================================================================
#
# Make some preliminary plots
#
#================================================================================
fignum = 0
fignames = []

# Average monthly temperature
fignames.append('amt'); pl.figure(fignum); fignum+=1
pl.ylabel(r"avg monthly temp [F]",fontsize=22,fontweight='bold')
plot_year_color_code(year_start,year_end,all_months,all_avg_monthly_temp)

# utilities paid
fignames.append('utilities'); pl.figure(fignum); fignum+=1
pl.ylabel(r"utility bill [\$]",fontsize=22,fontweight='bold')
plot_year_color_code(year_start,year_end,utility_months,utilities)

# ccf used
fignames.append('ccf'); pl.figure(fignum); fignum+=1
pl.ylabel(r"gas usage [ccf]",fontsize=22,fontweight='bold')
plot_year_color_code(year_start,year_end,utility_months,ccf)

# Default formatting of plots
default_formats_figures(fignum)

# save all the figures
save_figures(fignames)

#================================================================================
#
# Scatter plots of ccf vs temp/hdd
#
#================================================================================

#
# avg temp
#
pl.figure(fignum); fignum+=1
pl.xlabel(r"avg monthly temp [F]",fontsize=22,fontweight='bold')
pl.ylabel(r"gas usage [ccf]",fontsize=22,fontweight='bold')
x_y_scatter(sorted_avg_temp,sorted_ccf,sorted_months,True)

# Legends
pl.text(35,  50,r"$1^{\text{st}}$ y.", ha='right', va='center',fontsize=22,fontweight='bold', color=cmap[0])
pl.text(13,335,r"$2^{\text{nd}}$ y.", ha='right', va='center',fontsize=22,fontweight='bold', color=cmap[1])
pl.text(18, 240,r"$3^{\text{d}}$ y.", ha='right', va='center',fontsize=22,fontweight='bold', color=cmap[2])

# other formats
pl.setp(pl.gca().get_xmajorticklabels(),fontsize=18,fontweight='bold');
pl.setp(pl.gca().get_ymajorticklabels(),fontsize=18,fontweight='bold');
pl.setp(pl.gca(),xlim=[0,80])
#pl.setp(pl.gca(),ylim=[0,350])
# pl.gca().set_xticks(np.arange(0,24,6))
# pl.gca().set_yticks(np.arange(0,7,2))
pl.gca().spines['right'].set_color('none')
pl.gca().spines['top'].set_color('none')
pl.gca().xaxis.set_ticks_position('bottom')
pl.gca().yaxis.set_ticks_position('left')

# save
pl.savefig(plotdir+'TvsC.pdf',format='pdf')
pl.savefig(plotdir+'TvsC.png',format='png')

#
# VS HDD
#
pl.figure(fignum); fignum+=1
pl.xlabel(r"monthly heating degrees [hdd]",fontsize=22,fontweight='bold')
pl.ylabel(r"gas usage [ccf]",fontsize=22,fontweight='bold')
x_y_scatter(sorted_hdd,sorted_ccf,sorted_months,True)

# Legends
pl.text(1280, 100,r"$1^{\text{st}}$ y.", ha='left', va='center',fontsize=22,fontweight='bold', color=cmap[0])
pl.text(1470, 325,r"$2^{\text{nd}}$ y.", ha='left', va='center',fontsize=22,fontweight='bold', color=cmap[1])
pl.text(1360, 230,r"$3^{\text{d}}$ y.", ha='left', va='center',fontsize=22,fontweight='bold', color=cmap[2])

# other formats
pl.setp(pl.gca().get_xmajorticklabels(),fontsize=18,fontweight='bold');
pl.setp(pl.gca().get_ymajorticklabels(),fontsize=18,fontweight='bold');
pl.setp(pl.gca(),xlim=[0,1800])
#pl.setp(pl.gca(),ylim=[0,350])
# pl.gca().set_xticks(np.arange(0,24,6))
# pl.gca().set_yticks(np.arange(0,7,2))
pl.gca().spines['right'].set_color('none')
pl.gca().spines['top'].set_color('none')
pl.gca().xaxis.set_ticks_position('bottom')
pl.gca().yaxis.set_ticks_position('left')

# save
pl.savefig(plotdir+'HDDvsC.pdf',format='pdf')
pl.savefig(plotdir+'HDDvsC.png',format='png')

#================================================================================
#
# Plot ccf per temp as a function of month
#
#================================================================================
pl.figure(fignum); fignum+=1
pl.xlabel(r"month of year",fontsize=22,fontweight='bold')
pl.ylabel(r"gas usage per temperature [ccf/K]",fontsize=22,fontweight='bold')
for k in range(0,delta_years):
    x = range(0,len(sorted_months[k]))
    y = ccf_per_temp[k,:len(sorted_months[k])]
    pl.plot(x,y,marker=markertype[k],ms=15,mfc=cmap[k],mec=cmap[k],ls='none')

# Label the ticks
list_tick_marks = [0,3,6,9,11] #range(0,12,2)
pl.gca().set_xticks(list_tick_marks)
pl.gca().set_xticklabels([month_labels[i] for i in list_tick_marks])

# format plot
pl.setp(pl.gca(),xlim=[-1,12])
pl.gca().spines['right'].set_color('none')
pl.gca().spines['top'].set_color('none')
pl.gca().xaxis.set_ticks_position('bottom')
pl.gca().yaxis.set_ticks_position('left')
pl.setp(pl.gca().get_xmajorticklabels(),fontsize=18,fontweight='bold');
pl.setp(pl.gca().get_ymajorticklabels(),fontsize=18,fontweight='bold');

# save
pl.savefig(plotdir+'usage_per_temp.pdf',format='pdf')
pl.savefig(plotdir+'usage_per_temp.png',format='png')


#================================================================================
#
# Plot ccf per hdd as a function of month
#
#================================================================================
pl.figure(fignum); fignum+=1
pl.xlabel(r"month of year",fontsize=22,fontweight='bold')
pl.ylabel(r"gas usage per monthly heating degree [ccf/hdd]",fontsize=22,fontweight='bold')
for k in range(0,delta_years):
    x = range(0,len(sorted_months[k]))
    y = ccf_per_hdd[k,:len(sorted_months[k])]
    pl.plot(x,y,marker=markertype[k],ms=15,mfc=cmap[k],mec=cmap[k],ls='none')

# Label the ticks
list_tick_marks = [0,3,6,9,11] #range(0,12,2)
pl.gca().set_xticks(list_tick_marks)
pl.gca().set_xticklabels([month_labels[i] for i in list_tick_marks])

# format plot
pl.setp(pl.gca(),xlim=[-1,12])
pl.gca().spines['right'].set_color('none')
pl.gca().spines['top'].set_color('none')
pl.gca().xaxis.set_ticks_position('bottom')
pl.gca().yaxis.set_ticks_position('left')
pl.setp(pl.gca().get_xmajorticklabels(),fontsize=18,fontweight='bold');
pl.setp(pl.gca().get_ymajorticklabels(),fontsize=18,fontweight='bold');

# save
pl.savefig(plotdir+'usage_per_hdd.pdf',format='pdf')
pl.savefig(plotdir+'usage_per_hdd.png',format='png')


#show()


