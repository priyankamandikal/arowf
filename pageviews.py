import sys
import requests
import traceback
from datetime import date, datetime, timedelta

article_url = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article'		# API url


def parse_date(stringDate):
	return datetime.strptime(stringDate.ljust(10,'0'), '%Y%m%d%H')	# convert string dates into datetime type


def format_date(d):
	return datetime.strftime(d, '%Y%m%d%H')							# convert datetime date to string type

def article_views(project, article, access='all-access', agent='all-agents', granularity='daily', start=None, end=None):

	
	endDate = end or date.today()					# set end date as today by default
	if type(endDate) is not date:
		endDate = parse_date(end)

	
	startDate = start or endDate - timedelta(30)	# set start date as 30 days before end date
	if type(startDate) is not date:
		startDate = parse_date(start)

	
	article = article.replace(' ', '_')				# replace  spaces with underscores
	url = '/'.join([article_url, project, access, agent, article, 'daily', format_date(startDate), format_date(endDate)])

	try:
		result = requests.get(url).json()
		last30dayscount = 0
		for item in result['items']:
			last30dayscount += item['views']
		print last30dayscount

	except:
		print 'Error while fetching and parsing ' + str(url)
		print traceback.format_exc()

if __name__ == '__main__':
	art = str(sys.argv[1])
	article_views('en.wikipedia', art)