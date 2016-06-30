import requests
from bs4 import BeautifulSoup
import traceback

url = 'https://en.wikipedia.org/wiki/Category:Wikipedia_articles_in_need_of_updating_from_May_2016'

try:
	r = requests.get(url)
	bs = BeautifulSoup(r.text)
	for catgroup in bs.find_all('div', 'mw-category-group'):
		for entry in catgroup.find_all('li'):
			a = entry.find('a')
			link = 'https://en.wikipedia.org' + a.get('href')
			title = a.get('title')
			print title
			print link
			print

except:
	print "Error while parsing backlogs"
	print traceback.format_exc()