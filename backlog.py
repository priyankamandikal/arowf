# -*- coding: utf-8 -*-

### denote lines that need to be changed for different categories

import sys
reload(sys)
sys.setdefaultencoding("utf-8")			# to handle UnicodeDecode errors

from math import ceil 					# top 20% of rankings
from traceback import format_exc		# to handle errors
import pickle				 			# to store article rankings
import json 							# for parsing the json response
from urllib2 import urlopen				# to load urls
from os import path, listdir
from operator import itemgetter			# to rank articles in the order of decreasing pageviews in a list
# from collections import OrderedDict		# to store articles in the order of decreasing pageviews in a dict
from pageviews import format_date, article_views	# to get pageviews

# cmlimit to specify number of articles to extract, max can be 500 (5000 for bots)
# cmtitle for name of Category to look in
# cmstartsortkeyprefix for starting the article listing from a particular alphabet or set of alphabets, 
# 'b' for PA outdated
category_api_url = 'https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmlimit=500&format=json&cmstartsortkeyprefix=m'	###
recdir = 'TL_records' + path.sep 	###


def nextrecord():
	try:
		records = listdir(recdir)
		record = 1+int(max(records)[:9])
		### todo: check for improperly named files
		return format(record, '09')
	except:
		return format(1, '09')


if __name__ == '__main__':

	#category_list = ['Category:All_Wikipedia_articles_in_need_of_updating', 
	#				'Category:All_NPOV_disputes']
	try:
		category_url = '&cmtitle='.join([category_api_url, 'Category:All_NPOV_disputes']) ###
		json_obj = urlopen(category_url).read()
	except:
		print "Error while obtaining articles from Category API"
		print format_exc()

	readable_json = json.loads(json_obj)
	cnt = 0
	d = []						# list of lists of rankings to be stored in a pickle file
	for ele in readable_json['query']['categorymembers']:
		title = ele['title']
		link = '/'.join(['https://en.wikipedia.org/wiki', title.replace(' ', '_')])
		categ = 'Category:All_NPOV_disputes'	###
		pageviews = article_views(title)
		print cnt+1, title, pageviews
		d.append([title, link, pageviews, categ])
		cnt = cnt+1

	# od = OrderedDict(sorted(d.items(), key=lambda t:t[1][1], reverse=True))	# ordered dict in descending order of final score
	od = sorted(d, key=itemgetter(2), reverse=True)	# ordered list in descending order of pageviews
	print '\n\nArticle rankings based on pageviews:\n'
	for item in od:
		print item
	#with open('npov_b_ranking.pkl', 'wb') as f:
	with open('TL_pickles/npov_m_ranking.pkl', 'wb') as f:	### 
		pickle.dump(od, f)

# if __name__ == '__main__':
# 	with open('PA_pickles/npov_m_ranking.pkl', 'rb') as f:	### use when od has already been created; comment above stuff
# 		od = load(f)
	cnt = 0		
	counter = int(ceil(0.2*len(od)))	# top 20% of rankings

	#url = 'http://127.0.0.1:5000/ask'	# url for POSTing to ask. Replace with Labs/PythonAnywhere instance if needed
	
	for i in od:

		# POSTing to ask
		# data = {'question':'The article '+i[1]+' is in https://en.wikipedia.org/wiki/'+i[3]+'.\nHow would you resolve it?\n'+i[3], 
		# 		'iframeurl':i[1]}
		# r = requests.post(url, data=data)
		
		fn = recdir + nextrecord() + 'q'
		print fn
		if path.exists(fn):
			print('A billion questions reached! Start answering!')
			exit()
		f = open(fn, 'w')
		# use 'How would you resolve it?' for NPOV and 'How would you update it?' for outdated
		f.write('The article <a href="' + i[1] + '">' + i[0] + 
			'</a> is in <a href = "https://en.wikipedia.org/wiki/'+ i[3] + '">' + i[3] + 
			'</a>. How would you resolve it?<br/><a style="float:right;" href="' + 
			i[1] + '">'+i[1]+'</a><iframe src="' + i[1] + 
			'" style="height: 40%; width: 100%;">[Can not display <a href="' + i[1] + '">' 
			+ i[1] + '</a> inline as an iframe here.]</iframe>')	###
		f.close()
		cnt += 1
		if (cnt == counter):
			exit()