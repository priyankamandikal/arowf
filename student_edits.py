# -*- coding: utf-8 -*-

# NOTE: Taking top 50% from rankings
### denote lines that need to be changed for different instances

import sys
reload(sys)
sys.setdefaultencoding("utf-8")			# to handle UnicodeDecode errors

import requests
from bs4 import BeautifulSoup
from math import ceil 					# top 50% of rankings
from traceback import format_exc		# to handle errors
import pickle				 			# to store article rankings
import json 							# for parsing the json response
from urllib2 import urlopen				# to load urls
from os import path, listdir
from operator import itemgetter			# to rank articles in the order of decreasing pageviews and sizes in a list
from pageviews import format_date, article_views	# to get pageviews
from numpy import mean, std 			# for computing standard scores

### different pages from Special:Students
# PA
# students_url = ['https://en.wikipedia.org/wiki/Special:Students',
# 				'https://en.wikipedia.org/w/index.php?title=Special:Students&offset=13589', 
# 				'https://en.wikipedia.org/w/index.php?title=Special:Students&offset=13538',
# 				'https://en.wikipedia.org/w/index.php?title=Special:Students&offset=13488',
# 				'https://en.wikipedia.org/w/index.php?title=Special:Students&offset=13438',
# 				'https://en.wikipedia.org/w/index.php?title=Special:Students&offset=13388',
# 				'https://en.wikipedia.org/w/index.php?title=Special:Students&offset=13338']

# TL
students_url = ['https://en.wikipedia.org/w/index.php?title=Special:Students&offset=13288',
				'https://en.wikipedia.org/w/index.php?title=Special:Students&offset=13238',
				'https://en.wikipedia.org/w/index.php?title=Special:Students&offset=13188',
				'https://en.wikipedia.org/w/index.php?title=Special:Students&offset=13138',
 				'https://en.wikipedia.org/w/index.php?title=Special:Students&offset=13088',
 				'https://en.wikipedia.org/w/index.php?title=Special:Students&offset=13038',
 				'https://en.wikipedia.org/w/index.php?title=Special:Students&offset=12988']


diff_url = 'https://en.wikipedia.org/w/index.php?diff=prev'

# ucnamespace of 0 is for only article edits (excludes talk pages, etc)
# most recent contribs first by default
# ucuser for username
# uclimit to specify max number contribs retreived, here top 5 for that contributor
usercontribs_api = 'https://en.wikipedia.org/w/api.php?action=query&list=usercontribs&ucnamespace=0&format=json&uclimit=2'

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

	cnt = 0
	d = []						# list of lists of rankings to be stored in a pickle file
	
	for url in students_url:
		try:
			r = requests.get(url)
			bs = BeautifulSoup(r.text)
		except:
			print "Error while obtaining student usernames"
			print format_exc()

		header = bs.find('tbody')
		for entry in header.find_all('tr'):
			a = entry.find('a')
			contributor = a.get('title').encode('utf8')[5:]
			usercontribs_url = '&ucuser='.join([usercontribs_api, contributor.replace(' ', '_')])
			try:
				json_obj = urlopen(usercontribs_url).read()
			except:
				print "Error while obtaining usercontribs for "+contributor
				print format_exc()	
			readable_json = json.loads(json_obj)
			if len(readable_json['query']['usercontribs']) == 0:	# no contributions
				continue
			for ele in readable_json['query']['usercontribs']:
				title = ele['title']
				link = '/'.join(['https://en.wikipedia.org/wiki', title.replace(' ', '_')])
				pageid = ele['pageid']	# pageid identifies article
				revid = ele['revid']	# identifies revision
				size = ele['size']		# number of bytes added/removed
				diff = '&oldid='.join(['&pageid='.join([diff_url, str(pageid)]), str(revid)]) 	# diff url
				pageviews = article_views(title)
				if (size == None):	# error while obtaining edit size
					print 'Error while obtaining edit size for pageid ' + str(pageid) + ' and revid ' + str(revid)
					continue
				if (pageviews == None):	# error while retreiving pageviews
					print 'Error while obtaining pageviews for ' + title
					continue
				print cnt+1, contributor, title, pageviews, size
				d.append([contributor, title, link, diff, pageviews, size])
				cnt = cnt+1
				if(cnt==200):
					break
			if(cnt==200):
					break

	pv = []
	size = []
	for i in d:
		pv.append(i[4])		# get all the pageviews
		size.append(i[5])	# get all the edit sizes
	mean_pv = mean(pv)		
	std_pv = std(pv)
	mean_size = mean(size)
	std_size = std(size)
	for i in d:
		i. append(float(format(float((i[4] - mean_pv)/std_pv) + float(((i[5] - mean_size)/std_size)), '.2f')))	#  to rank higher in severity, article should rank high in pageview and edit size
	od = sorted(d, key=itemgetter(6), reverse=True)	# ordered list in descending order of final score
	#print '\n\nArticle rankings based on final score:\n'
	#for item in od:
	#	print item
	with open('TL_pickles/student_edits_ranking.pkl', 'wb') as f:
		pickle.dump(od, f)


# if __name__ == '__main__':
# 	with open('TL_pickles/student_edits_ranking.pkl', 'rb') as f:	### use when od has already been created; comment above stuff
# 		od = pickle.load(f)
	cnt = 0		
	counter = int(ceil(0.5*len(od)))	# top 50% of rankings
	
	#url = 'http://127.0.0.1:5000/ask'	# url for POSTing to ask. Replace with Labs/PythonAnywhere instance if needed
	
	for i in od:
		
		# POSTing to ask
		# data = {'question':'The article '+i[2]+' was edited by a student editor.\nThe diff corresponding to the edit is displayed below. Does it look alright?\n'+i[3], 
		#		'iframeurl':i[3]}
		# r = requests.post(url, data=data)
		
		fn = recdir + nextrecord() + 'q'
		print fn
		if path.exists(fn):
			print('A billion questions reached! Start answering!')
			exit()
		f = open(fn, 'w')
		f.write('The article <a target="_blank" href="' + i[2] + '">' + i[1] + 
			'</a> was edited by a student editor.</br>The diff corresponding to the edit is displayed below. Has it been correctly edited?<br/><a target="_blank" style="float:right;" href="'
			+ i[3] + '">' + i[3] + '</a><iframe src="' + i[3] + 
			'" style="height: 40%; width: 100%">[Can not display <a target="_blank" href="' + i[3] + '">' + i[3] 
			+ '</a> inline as an iframe here.]</iframe>')
		f.close()
		cnt += 1
		if (cnt == counter):
			exit()

	