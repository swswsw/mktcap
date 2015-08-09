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