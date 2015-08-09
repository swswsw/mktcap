import webapp2
import urllib2
import urllib
import json

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
			self.response.write(jsonResult)

			self.insert('dailymktcap', textResult)
		except urllib2.URLError, e:
			print e.reason
	
	# insert data to mongolab
	def insert(self, collection, textResult):
		# save to mongodb

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

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/daily_task', DailyTask),
], debug=True)