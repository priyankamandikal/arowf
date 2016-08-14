import requests
from bs4 import BeautifulSoup
import traceback
from os import path, listdir
import sys
from pageviews import format_date, article_views

# to access functions from python files in another directory
sys.path.insert(0,'/home/priyanka/Documents/Wikipedia_Accuracy_Review/wikiwho_api/wikiwho_api')

from wikiwho_api_api import mainFunction

# can set parameters such as limit, offset, etc
url = 'https://en.wikipedia.org/w/index.php?title=Special:Search&limit=20&offset=0&profile=default&search=recently'
categ = path.basename(url)

recdir = 'records' + path.sep

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
        bs = BeautifulSoup(r.text)
        cnt = 0;
        results = bs.find('ul', 'mw-search-results')
        for entry in results.find_all('li'):
            
            try:
                heading = entry.find('div','mw-search-result-heading')
                link = "https://en.wikipedia.org" + heading.a.get('href')
                title = heading.a.get('title')
                if 'recently' in title.lower():
                    continue
                #print link
                #print title
                pageviews = article_views(title)
                content = entry.find('div','searchresult')
                context = content.contents[0] + '<b>'+content.contents[1].contents[0]+'</b>' + content.contents[2]
                d[title] = [link, pageviews, context]

            except:
                print "Error while parsing article " + title
                print traceback.format_exc()

    except:
        print 'Error while extracting data'
        print traceback.format_exc()

        
    od = OrderedDict(sorted(d.items(), key=lambda t:t[1][1], reverse=True)) # ordered dict in descending order of final score
    print '\n\nArticle rankings based on pageviews:\n'
    for item in od.items():
        print item
    with open('recently_ranking.pkl', 'wb') as f:
        dump(od, f)

# if __name__ == '__main__':
#   with open('recently_ranking.pkl', 'rb') as f:  # use when od has already been created; comment above stuff
#       od = load(f)
    cnt = 0     
    counter = int(ceil(0.2*len(od)))    # top 20% of rankings

    #url = 'http://127.0.0.1:5000/ask'   # url for POSTing to ask. Replace with Labs/PythonAnywhere instance if needed
    
    for i in od.items():

        # importing function from wikiwho_api_api.py. This uses the findWord function in Wikiwho_simple.py
        date = mainFunction(title)

        # POSTing to ask
        # data = {'question':'The article '+i[1][0]+' has the word 'recently' inserted in '+date+'. Is it still correctly used? The context is:\n'+i[1][2], 
        #       'iframeurl':i[1][0]}
        # r = requests.post(url, data=data)

        fn = recdir + nextrecord() + 'q'
        if path.exists(fn):
            print('A billion questions reached! Start answering!')
            exit()

        f = open(fn, 'w')
        f.write('The article <a href="' + i[1][0] + '">' + i[0] + 
            '</a> has the word \'recently\' inserted in ' + date +
            '. Is it still correctly used? The context is:</br><i>' + i[1][2] + 
            '</i></br><div style="border:1px solid black;"><a href="'+i[1][0]+'">'+i[1][0]+'</a><iframe src="' + i[1][0] + 
            '" style="height: 40%; width: 100%;">[Can not display <a href="' + 
            i[1][0] + '">' + i[1][0] + '</a> inline as an iframe here.]</iframe></div>')
        f.close()
        cnt += 1
        if (cnt == counter):
            exit()


    
