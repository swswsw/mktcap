import webapp2
import urllib2
import urllib
import json
import time
import datetime

url = 'http://coinmarketcap-nexuist.rhcloud.com/api/all'

# see this to obtain apikey http://docs.mongolab.com/data-api/
mongolablApiKey = '<apikey>'
dbname = 'mktcap'

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.write('hello, world')

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

		except urllib2.URLError, e:
			print e.reason
	
	# insert data to mongolab
	def insert(self, collection, textResult):
		''' save to mongodb '''

		insertApiUrlTemplate = 'https://api.mongolab.com/api/1/databases/{database}/collections/{collection}?apiKey={apiKey}'

		insertApiUrl = insertApiUrlTemplate.replace('{apiKey}', mongolablApiKey);
		insertApiUrl = insertApiUrl.replace('{database}', dbname);
		insertApiUrl = insertApiUrl.replace('{collection}', collection);

		# depending on the data type, urlencode may be necessary
		#data = urllib.urlencode({'login' : 'MyLogin', 'password' : 'MyPassword'})
		#data = json.dumps({'login' : 'MyLogin', 'password' : 'MyPassword'})
		data = textResult
		req2 = urllib2.Request(insertApiUrl, data, {'Content-Type': 'application/json'});
		resp2 = urllib2.urlopen(req2);
		print resp2.read()
		resp2.close()

	def getTotal(self, jsonResult):
		''' calculate total marketcap '''
		totalMktCap = 0
		for key in jsonResult:
			mktcap = float(jsonResult[key]['market_cap']['usd'])
			totalMktCap += mktcap
		print 'total mkt cap=' + str(totalMktCap)
		return totalMktCap

		

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/daily_task', DailyTask),
], debug=True)