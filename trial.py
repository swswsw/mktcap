float(jsonResult['Bitcoin']['market_cap']['usd'])



totalMktCap = 0
for key in jsonResult:
	mktcap = float(jsonResult[key]['market_cap']['usd'])
	totalMktCap += mktcap

print 'total mkt cap=' + str(totalMktCap)

btcMktCap = 0

if 'Bitcoin' in jsonResult:
	btcMktCap = float(jsonResult['Bitcoin']['market_cap']['usd'])

print 'btc mkt cap=' + str(btcMktCap)
print 'btc mkt percentage=' + str(btcMktCap / totalMktCap) 




# save to mongodb

insertApiUrlTemplate = 'https://api.mongolab.com/api/1/databases/{database}/collections/{collection}?apiKey={apiKey}'
mongolablApiKey = '<apikey>'
dbname = 'test1'
collection = 'trial1'

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

