# -*- coding: utf-8 -*-
"""
Created on Thu May  7 15:56:47 2020
Version 2020-05-13

@author: Harald

Instruction:

1. perform overpass-turbo (http://overpass-turbo.eu/) with the following query
(adapt [admin_level=8][name="Böblingen"] ! )

[out:csv(::id,::type,type,route,name,description,from,to)][timeout:25];
area[admin_level=8][name="Böblingen"]->.searchArea;
(
  rel[type=route][route=bicycle](area.searchArea);
  rel[type=route][route=hiking](area.searchArea);
);
out body;

2. store result in textfile like xxx.txt
3. change ifile (about line 140) to xxx.txt
4. run program
   results are in xxx_res.txt, can be read into Excel

"""

import os
import urllib.request
import time, datetime
from os.path import join, getsize, getmtime
# https://docs.python.org/3/library/os.path.html

# ==========================================================================
def ageofFile(filename):
    agetest = 0
    if agetest: print('asctime: ',time.asctime())
    nowtime = time.time()
    if agetest: print('act time: ',nowtime)
    lastm=os.path.getmtime(filename)
    if agetest: print('last mod:',lastm)
    if agetest: print('last mod:',time.ctime(lastm))

    diffsec= nowtime -lastm
    if agetest: print('diff [s]: ',int(diffsec))

    diffhour= diffsec / 3600
    if agetest: print('diff [h]: ',int(diffhour*10)/10.0)
    return(diffhour)

# ==========================================================================
def callRA(reln):
    test = 0
    maxage = 24.0   # if file is older than age hours, re-analyse data
    tmp_filename = 'data/rel'+str(reln)+'.html'
    url_ra='http://ra.osmsurround.org/analyzeRelation?relationId='+str(reln)+'&noCache=true&_noCache=on'

    # try to read local file
    found = 1
    try:
        infile = open(tmp_filename,'r')

    except FileNotFoundError:
        if test : print('local file '+tmp_filename+' not found')
        found = 0

    if found == 1 :
        age = ageofFile(tmp_filename)
        print('age of file [h]: ',int(age*10)/10.0,maxage)
        if age > maxage:
            print(tmp_filename,' to old')
            found = 0     # get new file

    # if not there get new data and store it
    if test : print('found final',found)
    if found == 0:
        if test : print('fetching data from extern')
        if test : print('reading from:',url_ra)

        with urllib.request.urlopen(url_ra) as response:
            data = str(response.read())
        tmp = open(tmp_filename,'w')
        tmp.write(data)
        tmp.close()
        time.sleep(2)
    else:
        if test : print('reading local data')
        data = infile.read()
        infile.close()

    lines = data.split('\\n')
    status = []

    for i in range(len(lines)):
 #       print(lines[i])
        if lines[i].find('In mehrere Teilgraphen getrennt') > 0:
            if test : print(lines[i])
            status = ['nicht zusammenhängend']
        if lines[i].find('Die Relation ist in Ordnung') > 0:
            if test : print(lines[i])
            status = ['zusammenhängend']
        if lines[i].find('p>Graph&nbsp;') > 0:
            pline = lines[i].replace('&auml;','ä')
            if test : print(pline)
            start = pline.find('(')
            end = pline.rfind(')')
            text = pline[start+1:end]
            status += [text]
    # if bad:
    #     print('Bad: In mehrere Teilgraphen getrennt')
    # else:
    #     print('Toll! Die Relation ist in Ordnung.')

    return(status)

# =====================================================================


# various tests
allrels =[5721903,8887999,1548473,5754]
allrels =[5721903]
# hiking in Gärtringen
allrels  = [31562,1377828,1840714,1972766,2415209,2438965,5738609,7902817,7902818]
allrels += [8089388,8089389,8089390,8089391,8887999,8888004,8888013]

# biking in Gärtringen
allrels  = [2161747,5569467,5569821,5658711,5709279,5709361,5717701,5717763,5718064,5756965]
allrels += [5864983,5906870,6267216,6340036,6352296,6352297,7902819,8379218]

title = 'hiking in VAI'
allrels  = [31979,31980,32728,105023,541184,1857338,1868413,1922413,1922414,2172998,2731146]
allrels += [3355053,4553165,4553218,4591826,5467349,7901482,7910229]
allrels = [6267216]

ifile = 'bike_HER.txt'
ifile = 'bike_EHN.txt'
ifile = 'bhike_BB.txt'
ifile = 'hike_HER.txt'
ifile = 'bhike_ALT.txt'
ifile = 'bhike_Nagold.txt'
ifile = 'bhike_S.txt'
ifile = 'BedarfStuttgart.txt'
ifile = 'BedarfBW.txt'

if len(ifile)>0:
    ofile = ifile.replace('.','_res.')
    outp = open(ofile,'w')
    title = ifile.replace('.txt','')

    with open(ifile) as inp :
        print('reading: ',ifile)
        indata = inp.read()
#        print(indata)

    print('writing: ',ofile)

    lines= indata.split('\n')
    lcnt = 0
    for sline in lines:
        words = sline.split('\t')
#        print(lcnt, words[0])
        if(words[0] == '@id'):
            oline = sline + '\t' + 'status' + '\t' + 'Länge Teilstücke'
            outp.writelines(oline+'\n')
        else:
            status=callRA(int(words[0]))
            oline = sline + '\t' + str(status[0])
            for x in status[1:]:
                oline += '\t' + str(x).replace('Länge in KM: ','')
            print(oline)
            outp.writelines(oline+'\n')
        lcnt += 1

    outp.writelines('Datum der Auswertung:     '+str(datetime.datetime.now())+'\n')
    outp.writelines('Auswertung dank: https://www.grundid.de/ und http://ra.osmsurround.org/index\n')

    outp.close()

else:
# print(allrels)
    print(title)

    for rel in allrels:
        status=callRA(rel)
        print('Relation:',rel,'   Status:',status)


