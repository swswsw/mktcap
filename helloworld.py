import webapp2
import urllib2
import urllib
import json

url = 'http://coinmarketcap-nexuist.rhcloud.com/api/all'

mongolabApiUrl = ''
mongolablApiKey = '<apikey>'
dbname = ''

class MainPage(webapp2.RequestHandler):
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
			



		except urllib2.URLError, e:
			print e.reason
		

app = webapp2.WSGIApplication([
	('/', MainPage),
], debug=True)