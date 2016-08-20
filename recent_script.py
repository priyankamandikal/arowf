# -*- coding: utf-8 -*-

### update in wikiwho_api_api.py as well

import sys
reload(sys)
sys.setdefaultencoding("utf-8")         # to handle UnicodeDecode errors

import requests
from bs4 import BeautifulSoup
from traceback import format_exc
from os import path, listdir
from math import ceil
import sys
#from collections import OrderedDict
from operator import itemgetter
import pickle
from datetime import datetime           # for arithmetic on dates
from numpy import mean, std             # for computing standard scores
from pageviews import format_date, article_views

# to access functions from python files in another directory
sys.path.insert(0,'/home/priyanka/Documents/Wikipedia_Accuracy_Review/wikiwho_api/wikiwho_api')

from wikiwho_api_api import mainFunction

# can set parameters such as limit, offset, etc
url = 'https://en.wikipedia.org/w/index.php?title=Special:Search&limit=500&offset=0&profile=default&search=recently' ###
categ = path.basename(url)

recdir = 'PA_records' + path.sep   ###

def nextrecord():
    try:
        records = listdir(recdir)
        record = 1+int(max(records)[:9])
        ### todo: check for improperly named files
        return format(record, '09')
    except:
        return format(1, '09')

if __name__ == '__main__':

    try:
        r = requests.get(url)
    except:
            print "Error while querying Special Search" + title
            print format_exc()
    bs = BeautifulSoup(r.text)
    cnt = 0
    d = []
    results = bs.find('ul', 'mw-search-results')

    for entry in results.find_all('li'):
        
        try:
            heading = entry.find('div','mw-search-result-heading')
            link = "https://en.wikipedia.org" + heading.a.get('href')
            title = heading.a.get('title')
            if 'recently' in title.lower():     # title should not contain recently
                continue
            pageviews = article_views(title)
            if (pageviews == None):
                print 'Error while obtaining pageviews for article ' + title
                continue
            content = entry.find('div','searchresult')
            context = content.contents[0] + '<b>'+content.contents[1].contents[0]+'</b>' + content.contents[2]
            date = mainFunction(title)  # importing function from wikiwho_api_api.py. This uses the findWord function in Wikiwho_simple.py
            if (date == None):
                print 'Error while obtaining date for article ' + title
                continue
            print cnt+1, title, pageviews, date     
            d.append([title,link, pageviews, context, str(date)])   # date is of type unicode
            cnt = cnt+1
            # if(cnt==500):
            #     break

        except:
            print "Error while parsing article " + title
            print format_exc()

   
    pv = []
    date = []
    for i in d:
        pv.append(i[2])     # get all the pageviews
        epoch = int(datetime.strptime(i[4], '%Y-%m-%d').strftime('%s'))
        date.append(epoch)  # get all the dates in epoch format for doing arithmetic operations on them
        i.append(epoch)     # appending epoch time to i 

    mean_pv = mean(pv)      
    std_pv = std(pv)
    mean_date = mean(date)
    std_date = std(date)
    for i in d:
        i. append(float(format(float((i[2] - mean_pv)/std_pv) - float(((i[5] - mean_date)/std_date)), '.2f')))  #  to rank higher in severity, article should rank high in pageview and low date epoch
    

    # od = OrderedDict(sorted(d.items(), key=lambda t:t[1][1], reverse=True)) # ordered dict in descending order of final score
    od = sorted(d, key=itemgetter(6), reverse=True) # ordered list in descending order of pageviews
    print '\n\nArticle rankings based on pageviews:\n'
    for item in od:
        print item
    with open('PA_pickles/recently_ranking.pkl', 'wb') as f:    ###
        pickle.dump(od, f)

# if __name__ == '__main__':
#     with open('PA_pickles/recently_ranking.pkl', 'rb') as f:  ### use when od has already been created; comment above stuff
#         od = pickle.load(f)
    cnt = 0     
    counter = 100 #int(ceil(0.25*len(od)))    # top 20% of rankings

    #url = 'http://127.0.0.1:5000/ask'   # url for POSTing to ask. Replace with Labs/PythonAnywhere instance if needed
    
    for i in od:

        # POSTing to ask
        # data = {'question':'The article '+i[1]+' has the word 'recently' inserted in '+i[4]+'. Is it still correctly used? The context is:\n'+i[3], 
        #       'iframeurl':i[1]}
        # r = requests.post(url, data=data)

        fn = recdir + nextrecord() + 'q'
        if path.exists(fn):
            print('A billion questions reached! Start answering!')
            exit()

        with open(fn, 'w') as f:
            try:
                f.write('The article <a href="' + i[1] + '">' + i[0] + 
                    '</a> has the word \'recently\' inserted in ' + i[4] +
                    '. Is it still correctly used? The context is:</br><i>' + i[3] + 
                    '</i></br><a style="float:right;" href="'+i[1]+'">'+i[1]+'</a><iframe src="' + i[1] + 
                    '" style="height: 40%; width: 100%;">[Can not display <a href="' + 
                    i[1] + '">' + i[1] + '</a> inline as an iframe here.]</iframe>')
                cnt = cnt + 1
            except:
                print 'Error while creating file'
                print format_exc()

            if (cnt == counter):
                exit()
