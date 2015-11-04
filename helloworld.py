import webapp2
import httplib
import urllib2
import urllib
import jinja2
import json
import time
import datetime
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

url = 'http://coinmarketcap-nexuist.rhcloud.com/api/all'

# see this to obtain apikey http://docs.mongolab.com/data-api/
mongolabApiKey = 'ixUcm0jaZOms1nQCxr3ixyS3Haq2VJhj'
dbname = 'mktcap'

class MainPage(webapp2.RequestHandler):
	def get(self):
		template_values = {};
		self.response.headers['Content-Type'] = 'text/html'
		template = JINJA_ENVIRONMENT.get_template('index.html')
		# see https://cloud.google.com/appengine/docs/python/gettingstartedpython27/templates
		self.response.write(template.render(template_values))

class DailyTask(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		#self.response.write('hello, world')

		# get data from coinmarketcap
		try:
			result = urllib2.urlopen(url)
			textResult = result.read()
			self.response.write(textResult)
			jsonResult = json.loads(textResult)

			# alternatively, don't switch to text, directly convert result to json
			# jsonResult = json.load(result)

			# we can write jsonResult directly, but we do dumps to do pretty print
			self.response.write(json.dumps(jsonResult, indent=2))

			# you want isoformat time for mongolab
			#_id = int(time.time()) # default value
			_id = datetime.datetime.utcnow().isoformat()
			if 'Bitcoin' in jsonResult:
				timestamp = jsonResult['Bitcoin']['timestamp']
				_id = datetime.datetime.fromtimestamp(timestamp).isoformat() #convert epoch time to iso format
			
			totalMktCap = int(self.getTotal(jsonResult))
			#todo: change _id to actual date
			jsonResult['_id'] = _id

			self.insert('dailymktcap', json.dumps(jsonResult))


			btcMktCap = 0

			if 'Bitcoin' in jsonResult:
				btcMktCap = int(float(jsonResult['Bitcoin']['market_cap']['usd']))

			print 'btc mkt cap=' + str(btcMktCap)
			print 'btc mkt percentage=' + str(btcMktCap * 100 / totalMktCap) # *100 to get percentage

			#todo: change _id to correct date
			summaryData = json.dumps({'_id': _id, 'btcMktCap': btcMktCap, 'top100MktCap': totalMktCap});

			self.insert('dailysummary', summaryData);

			self.insertToday(_id, btcMktCap, totalMktCap)

		except urllib2.URLError, e:
			print e.reason
	
	# insert data to mongolab
	def insert(self, collection, textResult):
		''' save to mongodb '''

		insertApiUrlTemplate = 'https://api.mongolab.com/api/1/databases/{database}/collections/{collection}?apiKey={apiKey}'

		insertApiUrl = insertApiUrlTemplate.replace('{apiKey}', mongolabApiKey);
		insertApiUrl = insertApiUrl.replace('{database}', dbname);
		insertApiUrl = insertApiUrl.replace('{collection}', collection);

		# depending on the data type, urlencode may be necessary
		#data = urllib.urlencode({'login' : 'MyLogin', 'password' : 'MyPassword'})
		#data = json.dumps({'login' : 'MyLogin', 'password' : 'MyPassword'})
		# remove '...' from the json property, otherwise, it cannot be stored in mongolab.  
		# since oct 30, 2015, coinmarketcap.com shortens long coin name to "xxxxxxxxxxx...".  
		# eg. "Mastercoin (Omni)" is shortened to "Mastercoin (..."
		data = textResult.replace('...', '');
		try:			
			req2 = urllib2.Request(insertApiUrl, data, {'Content-Type': 'application/json'});
			resp2 = urllib2.urlopen(req2);
			print resp2.read()
			resp2.close()
		except urllib2.URLError, e:
			print e.reason

	def update(self, collection, data):
		'''update mongodb record'''
		print 'update'
		# use httplib because urllib2 is not good with put
		uri = '/api/1/databases/{database}/collections/{collection}/alldays?apiKey={apiKey}'

		uri = uri.replace('{apiKey}', mongolabApiKey);
		uri = uri.replace('{database}', dbname);
		uri = uri.replace('{collection}', collection);

		connection =  httplib.HTTPSConnection('api.mongolab.com')
		connection.request('PUT', uri, data, {'Content-Type': 'application/json'})
		resp = connection.getresponse()
		print resp
		print resp.read();
		




	def insertToday(self, isodatetime, btcMktCap, totalMktCap):
		'''
		insert the data for today into the record
		'''
		# mongo provides way to insert into array, but mongolab rest api does not have that.
		# so we will read and update the whole record.

		# read first.
		collection = 'alldays';
		readUrl = 'https://api.mongolab.com/api/1/databases/{database}/collections/{collection}/alldays?apiKey={apiKey}'
		readUrl = readUrl.replace('{apiKey}', mongolabApiKey);
		readUrl = readUrl.replace('{database}', dbname);
		readUrl = readUrl.replace('{collection}', collection);
		
		# default value in case record does not exist yet. 
		newElem = [isodatetime, btcMktCap, totalMktCap]
		jsonResult = json.dumps({'_id': "alldays", 'data': [[isodatetime, btcMktCap, totalMktCap]]});
		try:
			result = urllib2.urlopen(readUrl)
			textResult = result.read()
			self.response.write(textResult)
			jsonResult = json.loads(textResult)

			jsonResult['data'].append(newElem)
			jsonResult = json.dumps(jsonResult)
			
		except urllib2.URLError, e:
			# could get 404 if record does not exist yet.  we can ignore 404.  
			print e.reason
		
		# write updated the record
		self.update(collection, jsonResult)

	def getTotal(self, jsonResult):
		''' calculate total marketcap '''
		totalMktCap = 0
		for key in jsonResult:
			mktcap = float(jsonResult[key]['market_cap']['usd'])
			totalMktCap += mktcap
		print 'total mkt cap=' + str(totalMktCap)
		return totalMktCap


class AllDays(webapp2.RequestHandler):
	'''
	displays data for all the days
	'''
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		#self.response.write('hello, world')

		# get data from mongo
		collection = 'alldays';
		readUrl = 'https://api.mongolab.com/api/1/databases/{database}/collections/{collection}/alldays?apiKey={apiKey}'
		readUrl = readUrl.replace('{apiKey}', mongolabApiKey);
		readUrl = readUrl.replace('{database}', dbname);
		readUrl = readUrl.replace('{collection}', collection);

		try:
			result = urllib2.urlopen(readUrl)
			textResult = result.read()
			self.response.write(textResult)

		except urllib2.URLError, e:
			# could get 404 if record does not exist yet.  we can ignore 404.  
			print e.reason


app = webapp2.WSGIApplication([
	('/', MainPage),
	('/dailytask', DailyTask),
	('/alldays', AllDays),
], debug=True)