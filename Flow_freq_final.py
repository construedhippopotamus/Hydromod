#FINAL
#Calculates return periods for existing condition flows.

#Calculate partial duration analysis for San Diego hydromod

# San Diego HMP Manual Ch 6, pg 6-25

# must have 24-hr dry between events
# dry = no rain greater than 0.01 cfs  --> check this against SDHM - cutoff appears to be somewhat arbitrary.
# return a dataset with peak Qs for each event, and the number of peaks.

# ASSUMPTIONS: Q data is continuous, hourly data with no gaps.

import os
import csv
import openpyxl
from openpyxl import Workbook

def Qprocess(path, datafile):

    low = 0.01
    sep = 24  #24hr between events

    date = []
    Q = []
    Qpart = []
    dry = 24  #number of dry hours - start at 24 to catch first event, which can occur at hr = 0
    peak = 0
    peaklist = []

    os.chdir(path)

    #Extract Qs from both output files.
    with open(datafile, 'r') as f:
        csvreader = csv.reader(f, delimiter = ' ')
        for row in csvreader:
            try:
                date.append(row[12]) #would need rows 1-3
                Q.append(float(row[23]))
            except ValueError:
                pass
            except IndexError:
                pass

    series = list(zip(date, Q))  #just need Qs if data is hourly, but leave for now.
    #print ("series", series)

    #HMP manual way of determining series:

    for event in series:
        if event[1] <= low:
            dry+= 1   #Count dry hour
        if event[1] > low:
            #print("rain", event[1])

            if dry >= 24:  #new event

                if peak > 0:
                    peaklist.append(peak)  # append peak from last event
                    #print("peak appended", peak)
                    peak = 0    #reset peak for current storm
            #else:   #same event because less than 24 dry hours have passed
            if event[1] > peak:
                peak = event[1]
                #print("current peak", peak)

            dry = 0  #reset dry hours
            
    #capture last peak
    peaklist.append(peak)
    
    print("Peaks: ", peaklist)

    #Calculate flow frequencies for San Diego hydromod

    # San Diego HMP Manual Ch 6, pg 6-25

    #1. sort values large to small
    #2. Flow frequency with Cunnane Eqn: Probability = P = (i-0.4)/(n+0.2)
    #   i = Position of the peak whose probability is desired
    #   n = number of years analyzed = 1-10 = 10

    #Calculate flow frequencies for San Diego hydromod

    # ASSUMPTIONS: number of peaks analyzed MUST be equal to n.

    #remove any duplicates
    peaklist1 = list(set(peaklist))
    #print("len w/o duplicates:", len(peaklist1), "orig len:", len(peaklist))

    #sort peak list
    peaklist1.sort(reverse = True)
    #print("Sorted peak list", peaklist1)

    #keep 57 largest Qs for analysis.
    del(peaklist1[57:])

    #Calculate Cunnane probability for 57 years of flow record at this gage
    n = 57 #years in flow record
    Returnlist = []   #list to store return periods

    for i in range(0, 57):
        #rank = i + 1
        P = ((i+1)-0.4) / (n+0.2)
        R = 1/ P  # return period
        Returnlist.append(R)


    rankQs = dict(zip(Returnlist, peaklist1))

    #print(rankQs)

    Q2 =  rankQs.get(2.0)
    Q10up = rankQs.get(10.214285714285715)
    Q10low = rankQs.get(8.666666666666668)
    
    #this is 101 comparison points technically... need to divide by 99 because zero is counted. Fix later.
    Q10 = Q10low + (10-8.666)* (Q10up - Q10low) / (10.214285714285715-8.666666666666668)

    #Make list of 100 comparison points from 0.1*Q2 --> Q100
    Qcompare = [(Q10 - 0.1*Q2)*y/99 + 0.1*Q2 for y in range(0, 100)]
	
    #print(datafile, "Q2", Q2, "Q10", Q10)  

    return Qcompare, Q


"""
#to test as stand-alone:
path = r'C:\Users\Pizzagirl\Documents\Michael Baker\SWMM-delpy\delpy'
#Existing condition Q out file from EPA SWMM 5
#datafile = r'TEST111.TXT'
datafile = 'PRE_DEV_POC-1_QOUT.TXT'
outputs = Qprocess(path,datafile)
#print outputs[0]
"""
