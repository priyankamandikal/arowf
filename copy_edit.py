# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")	# to handle UnicodeDecode errors

import requests
from math import ceil
from traceback import format_exc
import re
import operator
import pickle
import json
from urllib2 import urlopen
from bs4 import BeautifulSoup
from os import path, listdir
from numpy import mean, std
from operator import itemgetter
from pageviews import format_date, article_views

# for fk scores
from utils import get_char_count
from utils import get_words
from utils import get_sentences
from utils import count_syllables
from utils import count_complex_words

# cmlimit to specify number of articles to extract, max can be 500 (5000 for bots)
# cmtitle for name of Category to look in
# cmstartsortkeyprefix for starting the article listing from a particular alphabet or set of alphabets, 
# 'p' for PA
copy_edit_url = 'https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmlimit=500&format=json&cmtitle=Category:All_articles_needing_copy_edit&cmstartsortkeyprefix=ap' ###

xml_api_url = 'https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&format=xml'
recdir = 'TL_records' + path.sep 	###


def nextrecord():
	try:
		records = listdir(recdir)
		record = 1+int(max(records)[:9])
		### todo: check for improperly named files
		return format(record, '09')
	except:
		return format(1, '09')


def flesch_kincaid_score(article):
	xml_url = '&titles='.join([xml_api_url, title])
	try:
		xml = requests.get(xml_url).content
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
			print format_exc()

	except:
		print 'Error while fetching xml content of ' + article
		print format_exc()
	
	


if __name__ == '__main__':

	try:
		json_obj = urlopen(copy_edit_url).read()
	except:
		print "Error while obtaining articles from Category API"
		print format_exc()
		exit()

	readable_json = json.loads(json_obj)
	cnt = 0
	d = []						# list of lists of rankings to be stored in a pickle file
	for ele in readable_json['query']['categorymembers']:
		title = ele['title'].encode('utf8')
		link = '/'.join(['https://en.wikipedia.org/wiki', title.replace(' ', '_')])
		pageviews = article_views(title)
		fk_score = flesch_kincaid_score(title)
		if (pageviews == None):
			print 'Error while obtaining pageviews for ' + title
			continue
		if (fk_score == None):
			print 'Error while obtaining F-K score for ' + title
			continue
		print cnt+1, title, link, pageviews, fk_score
		d.append([title, link, pageviews, fk_score])
		cnt = cnt+1

	pv = []
	fk = []
	for i in d:
		pv.append(i[2])		# get all the pageviews
		fk.append(i[3])		# get all the fk-scores
	mean_pv = mean(pv)		
	std_pv = std(pv)
	mean_fk = mean(fk)
	std_fk = std(fk)
	for i in d:	# here i is a list of [title, link, pv, fk]
		i. append(format(float((i[2] - mean_pv)/std_pv) - float(((i[3] - mean_fk)/std_fk)), '.2f'))	#  to rank higher in severity, article should rank high in pageview and low on fk score
		print i
	#od = OrderedDict(sorted(d.items(), key=lambda t:t[1][3], reverse=True))	# ordered dict in descending order of final score
	od = sorted(d, key=itemgetter(4), reverse=True)		# ordered list in descending order of final score
	#print '\n\nArticle rankings based on final score:\n'
	#for item in od:
	#	print item
	with open('TL_pickles/copy_edit_ap_ranking.pkl', 'wb') as f:
		pickle.dump(od, f)
# if __name__ == '__main__':
# 	with open('PA_pickles/copy_edit_ranking.pkl', 'rb') as f:	### use when od has already been created; comment above stuff
# 		od = pickle.load(f)
	cnt = 0		
	counter = int(ceil(0.25*len(od)))	# top 20% of rankings

	#url = 'http://127.0.0.1:5000/ask'	# url for POSTing to ask. Replace with Labs/PythonAnywhere instance if needed
	
	for i in od:
		
		# POSTing to ask
        # data = {'question':'The article '+i[1][0]+' is too wordy with a median Flesh-Kincaid readability score of '+str(i[1][2])+'. How would you rewrite it to be easier to read?', 
        #       'iframeurl':i[1][0]}
        # r = requests.post(url, data=data)

		fn = recdir + nextrecord() + 'q'
		print fn
		if path.exists(fn):
			print('A billion questions reached! Start answering!')
			exit()
		f = open(fn, 'w')
		f.write('The article <a target="_blank" href="' + i[1] + '">' + i[0] + 
			'</a> is too wordy with a median <a target="_blank" href = "https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch_reading_ease">Flesh-Kincaid readability score</a> of ' 
			+ str(i[3]) + '.</br>How would you rewrite it to be easier to read?<br/><a style="float:right;" href="'
			+ i[1] + '">' + i[1] + '</a><iframe src="' + i[1] + 
			'" style="height: 40%; width: 100%">[Can not display <a target="_blank" href="' + i[1] + '">' + i[1] 
			+ '</a> inline as an iframe here.]</iframe>')
		f.close()
		cnt += 1
		if (cnt == counter):
			exit()
