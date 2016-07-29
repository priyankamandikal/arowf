import requests
from bs4 import BeautifulSoup
import traceback
from os import path, listdir
import sys

# to access functions from python files in another directory
sys.path.insert(0,'/home/priyanka/Documents/Wikipedia_Accuracy_Review/wikiwho_api/wikiwho_api')

from wikiwho_api_api import mainFunction

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
                print
                heading = entry.find('div','mw-search-result-heading')
                link = "https://en.wikipedia.org" + heading.a.get('href')
                title = heading.a.get('title')
                if 'recently' in title.lower():
                    continue
                print link
                print title
                content = entry.find('div','searchresult')
                context = content.contents[0] + '<b>'+content.contents[1].contents[0]+'</b>' + content.contents[2]
                fn = recdir + nextrecord() + 'q'
                print fn
                if path.exists(fn):
                    print('A billion questions reached! Answer!')
                    exit()

                # importing function from wikiwho_api_api.py. This uses the findWord function in Wikiwho_simple.py
                date = mainFunction(title)
                f = open(fn, 'w')
                f.write('The article <a href="' + link + '">' + title + 
                    '</a> has the word \'recently\' inserted in ' + date +
                    '. Is it still correctly used? The context is:</br><i>' + context + 
                    '</i></br><iframe src="' + link + 
                    '" align=right style="height: 40%; width: 80%;">[Can not display <a href="' + 
                    link + '">' + link + '</a> inline as an iframe here.]</iframe>')
                f.close()
                cnt = cnt+1
                if(cnt==5):
                    sys.exit()

            except SystemExit:
                print cnt , ' question files created\nExiting'
                sys.exit()

            except:
                print "Error while parsing article " + title
                print traceback.format_exc()
    
    except SystemExit:
        sys.exit()

    except:
        print 'Error while extracting data'
        print traceback.format_exc()
