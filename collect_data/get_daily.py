import requests
import json
from datetime import datetime, timedelta
import pandas as pd 
from sqlalchemy.types import Text
from sqlalchemy import create_engine
import os

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

API_KEY = '2GFOZA03lLhqa9RNkc3geFiPwmANTspf'

cwd = os.getcwd()

ticker_list = os.path.join(cwd, 'tickers', 'tickers.txt')

log = os.path.join(cwd, 'collect_data', 'daily_log.txt')

d = open(log, 'r')
start_string = d.readline().strip()
d.close()
today = datetime.now()
today_string = today.strftime('%Y-%m-%d')
end_date = today + timedelta(days=-1)
end_string = end_date.strftime('%Y-%m-%d')

tracker = os.path.join(cwd, 'tickers/tracker', '{}.txt'.format(today_string))

track = open(tracker, 'w')

errors = 0

dataframe = {
			'ticker': [], 
			'close': [],
			'high': [], 
			'low': [], 
			'open': [], 
			'transactions': [], 
			'time': [], 
			'date': [], 
			'volume': [],
			'avg price': []}

def add_to_log(date):
	with open(log, 'r+') as f:
		content = f.read()
		f.seek(0)
		f.write(date + '\n' + content)
		f.flush()

def collect():

	headers = {'Authorization' : 'Bearer {}'.format(API_KEY)}

	print('TimeFrame')
	print(start_string)
	print(end_string)
	print("STARTING ...")

	with open(ticker_list, 'r') as file:

		for temp in file:

			ticker = temp.strip()

			url = 'https://api.polygon.io/v2/aggs/ticker/{}/range/1/day/{}/{}?adjusted=true&sort=asc&limit=50000&apiKey={}'.format(ticker, start_string, end_string, API_KEY)
			r = requests.get(url, headers = headers)
			message = extract(r.json(), ticker)
			track.write(message)
			track.flush()

	track.write('errors: {}'.format(errors))

	df = pd.DataFrame(data = dataframe)
	df.to_sql('daily', engine, if_exists = 'append', index = False)

	add_to_log(today_string)
	print("DONE")

def extract(data, ticker):

	if data['resultsCount'] > 0:

		try: 

			print(data)

			for x in data['results']:
				date = datetime.fromtimestamp(x['t']/1000.0)

				dataframe['ticker'].append(ticker)
				dataframe['close'].append(x['c'])
				dataframe['high'].append(x['h'])
				dataframe['low'].append(x['l'])
				dataframe['open'].append(x['o'])
				dataframe['transactions'].append(x['n'])
				dataframe['time'].append(x['t'])
				dataframe['date'].append(date)
				dataframe['volume'].append(x['v'])
				dataframe['avg price'].append(x['vw'])
			
			return "{} done\n".format(ticker)

		except:
			errors += 1
			return "{} error\n".format(ticker)

	else:
		return "{} no data\n".format(ticker)


def main():
	collect()
	track.close()
	

if __name__ == '__main__':
	main()



import yfinance as yf 
from datetime import datetime, timedelta
import pandas as pd 
from sqlalchemy.types import Text
from sqlalchemy import create_engine

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

f = open("ticker_list.txt", "r")

for line in f:

	ticker = line.strip()

	data = yf.download(ticker, period = "1y", interval = "1d", group_by = 'ticker', prepost = True)
	data["Ticker"] = ticker
	data['Datetime'] = data.index
	data.to_sql('day', engine, if_exists = 'append', index = False)
	print(data)

	print(ticker)

f.close()


yf.download("SPY AAPL", start="2017-01-01", end="2017-04-30")
