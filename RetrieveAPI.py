import requests

request = requests.get('https://www.alphavantage.co/query?function=OVERVIEW&symbol=AIG&apikey=2KMJ76XV3WQ5M9K7')

data = request.json()

print('The current Book Value of AIG is ' + data['BookValue'] + ' and the Earnings per share figure is ' + data['EPS'] + '.')
