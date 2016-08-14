from datetime import date, datetime, timedelta
from traceback import format_exc
from requests import get

pageviews_url = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article'

def format_date(d):
	return datetime.strftime(d, '%Y%m%d%H')	


def article_views(article, project='en.wikipedia', access='all-access', agent='all-agents', granularity='daily', start=None, end=None):
	endDate = date.today()
	startDate = endDate - timedelta(30)
	url = '/'.join([pageviews_url, project, access, agent, article, 'daily', format_date(startDate), format_date(endDate)])
	try:
		result = get(url).json()
		last30dayscount = 0
		for item in result['items']:
			last30dayscount += item['views']
		return last30dayscount
	except:
		print 'Error while fetching page views of ' + article
		print format_exc()