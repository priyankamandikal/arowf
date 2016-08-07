# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")	# to handle UnicodeDecode errors

import requests
import math
import traceback
import re
import operator
import pickle
from bs4 import BeautifulSoup
from os import path, listdir
from datetime import date, datetime, timedelta
from numpy import mean, std
from collections import OrderedDict
from operator import itemgetter

# for fk scores
from utils import get_char_count
from utils import get_words
from utils import get_sentences
from utils import count_syllables
from utils import count_complex_words


copy_edit_url = 'https://en.wikipedia.org/wiki/Category:All_articles_needing_copy_edit'
xml_api_url = 'https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&format=xml'
pageviews_url = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article'

recdir = 'records' + path.sep


def nextrecord():
	try:
		records = listdir(recdir)
		record = 1+int(max(records)[:9])
		### todo: check for improperly named files
		return format(record, '09')
	except:
		return format(1, '09')


def format_date(d):
	return datetime.strftime(d, '%Y%m%d%H')	


def article_views(article, project='en.wikipedia', access='all-access', agent='all-agents', granularity='daily', start=None, end=None):
	endDate = date.today()
	startDate = endDate - timedelta(30)
	url = '/'.join([pageviews_url, project, access, agent, article, 'daily', format_date(startDate), format_date(endDate)])
	try:
		result = requests.get(url).json()
		last30dayscount = 0
		for item in result['items']:
			last30dayscount += item['views']
		return last30dayscount
	except:
		print 'Error while fetching page views of ' + article
		print traceback.format_exc()


def flesch_kincaid_score(article):
	xml_url = '&titles='.join([xml_api_url, title])
	try:
		xml = requests.get(xml_url).content
	except:
		print 'Error while fetching xml content of ' + article
		print traceback.format_exc()
	
	bs = BeautifulSoup(xml)
	try:
		text = str(bs.find('extract').contents[0].encode('utf-8'))	# convert NavigableString to string after encoding
		non_text = ['== See also ==\n', '== References ==\n', ' === Further references ===\n', '== External links ==\n', '== Notes ==\n']
		for ele in non_text:
			text = text.split(ele, 1)[0]
		text = re.sub('==.*==', '', text)
		words = get_words(text)
		syllableCount = count_syllables(text)
		sentences = get_sentences(text)
		fk = 206.835 - 1.015*len(words)/len(sentences) - 84.6*(syllableCount)/len(words)

		return float(format(fk,'.2f'))
	except:
		print 'Error while computing fk score of ' + article
		print traceback.format_exc()


if __name__ == '__main__':

	try:
		r = requests.get(copy_edit_url)
	except:
		print "Error while obtaining copy-edit backlogs"
		print traceback.format_exc()

	bs = BeautifulSoup(r.text)
	cnt = 0
	d = {}
	print '\nFetching articles from the copy-edit backlog category:\n'
	for catgroup in bs.find_all('div', 'mw-category-group'):
		for entry in catgroup.find_all('li'):
			a = entry.find('a')
			link = 'https://en.wikipedia.org' + a.get('href')
			title = a.get('title').encode('utf8')
			pageviews = article_views(title)
			fk_score = flesch_kincaid_score(title)
			print title, link, pageviews, fk_score
			d[title] = [link, pageviews, fk_score]
			cnt = cnt+1
			if(cnt==25):
				break
		if(cnt==25):
				break

	pv = []
	fk = []
	for i in d.values():
		pv.append(i[1])
		fk.append(i[2])
	mean_pv = mean(pv)
	std_pv = std(pv)
	mean_fk = mean(fk)
	std_fk = std(fk)
	for i in d.values():
		i. append(format(float((i[1] - mean_pv)/std_pv) - float(((i[2] - mean_fk)/std_fk)), '.2f'))	#  to rank higher in severity, article should rank high in pageview on low on fk score
		print i
	od = OrderedDict(sorted(d.items(), key=lambda t:t[1][3], reverse=True))	# ordered dict in descending order of final score
	print '\n\nArticle rankings based on final score:\n'
	for item in od.items():
		print item
	with open('copy_edit_ranking'+'.pkl', 'wb') as f:
		pickle.dump(od, f)
# if __name__ == '__main__':
# 	with open('copy_edit_ranking.pkl', 'rb') as f:	# use when od has already been created; comment above stuff
# 		od = pickle.load(f)
	cnt = 0		
	counter = int(math.ceil(0.2*len(od)))	# top 20% of rankings
	for i in od.items():
		fn = recdir + nextrecord() + 'q'
		print fn
		if path.exists(fn):
			print('A billion questions reached! Answer!')
			exit()
		f = open(fn, 'w')
		f.write('The article <a href="' + i[1][0] + '">' + i[0] + '</a> is too wordy with a median <a href = "https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch_reading_ease">Flesh-Kincaid readability score</a> of ' + str(i[1][2]) + '.</br>How would you rewrite it to be easier to read?<br/><iframe src="' + i[1][0] + '" align=right style="height: 40%; width: 80%;">[Can not display <a href="' + i[1][0] + '">' + i[1][0] + '</a> inline as an iframe here.]</iframe>')
		f.close()
		cnt += 1
		if (cnt == counter):
			exit()
