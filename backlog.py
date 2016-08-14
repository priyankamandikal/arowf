# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")			# to handle UnicodeDecode errors

from math import ceil 					# top 20% of rankings
from traceback import format_exc		# to handle errors
import pickle				 			# to store article rankings
import json 							# for parsing the json response
from urllib2 import urlopen				# to load urls
from os import path, listdir
from collections import OrderedDict		# to store articles in the order of decreasing pageviews in a dict
from pageviews import format_date, article_views	# to get pageviews

# cmlimit to specify number of articles to extract, max can be 500 (5000 for bots)
# cmtitle for name of Category to look in
# cmstartsortkeyprefix for starting the article listing from a particular alphabet or set of alphabets
category_api_url = 'https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmlimit=5&format=json&cmstartsortkeyprefix=b'
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

	#category_list = ['Category:All_Wikipedia_articles_in_need_of_updating', 
	#				'Category:All_NPOV_disputes']
	try:
		category_url = '&cmtitle='.join([category_api_url, 'Category:All_NPOV_disputes'])
		json_obj = urlopen(category_url).read()
	except:
		print "Error while obtaining articles from Category API"
		print format_exc()

	readable_json = json.loads(json_obj)
	d = {}
	for ele in readable_json['query']['categorymembers']:
		title = ele['title']
		link = '/'.join(['https://en.wikipedia.org/wiki', title.replace(' ', '_')])
		categ = 'Category:All_NPOV_disputes'
		pageviews = article_views(title)
		d[title] = [link, pageviews, categ]

	od = OrderedDict(sorted(d.items(), key=lambda t:t[1][1], reverse=True))	# ordered dict in descending order of final score
	print '\n\nArticle rankings based on pageviews:\n'
	for item in od.items():
		print item
	#with open('update_b_ranking.pkl', 'wb') as f:
	with open('npov_b_ranking.pkl', 'wb') as f:
		pickle.dump(od, f)

# if __name__ == '__main__':
# 	with open('backlog_ranking.pkl', 'rb') as f:	# use when od has already been created; comment above stuff
# 		od = load(f)
	cnt = 0		
	counter = int(ceil(0.2*len(od)))	# top 20% of rankings
	for i in od.items():
		fn = recdir + nextrecord() + 'q'
		print fn
		if path.exists(fn):
			print('A billion questions reached! Start answering!')
			exit()
		f = open(fn, 'w')
		f.write('The article <a href="' + i[1][0] + '">' + i[0] + 
			'</a> is in <a href = "https://en.wikipedia.org/wiki/'+ i[1][2] + '">' + i[1][2] + 
			'</a>. How would you update it?<br/><div style="border:1px solid black;"><a href="' + 
			i[1][0] + '">'+i[1][0]+'</a><iframe src="' + i[1][0] + 
			'" style="height: 40%; width: 100%;">[Can not display <a href="' + i[1][0] + '">' 
			+ i[1][0] + '</a> inline as an iframe here.]</iframe></div>')
		f.close()
		cnt += 1
		if (cnt == counter):
			exit()