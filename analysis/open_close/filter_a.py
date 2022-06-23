# filter a:
# compiles a list of tickers that meet the following criteria:
# - price >= $100
# - volume >= 1000000
# - do not touch close_open when negative
# - analyze premarket

import pandas as pd 
from sqlalchemy.types import Text
from sqlalchemy import create_engine

import matplotlib
import matplotlib.pyplot as plt

import numpy as np
from scipy.stats import norm
import statistics

from datetime import datetime

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

today = datetime.now()
today_string = today.strftime('%Y-%m-%d')

tentative = '../../tickers/tentative/{}.txt'.format(today_string)
ticker_list = '../../tickers/tickers.txt'

price_limit = 100
volume_limit = 500000

limit = 30

def get_data(ticker):
	sql = """
			SELECT * FROM daily 
			WHERE Ticker = "{}"
			ORDER BY time DESC
			LIMIT {}
		""".format(ticker, limit)

	df = pd.read_sql(sql, engine)

	return df

def high_price_volume():

	with open(tentative, 'w') as f, open(ticker_list, 'r') as t:

		for temp in t:
			ticker = temp.strip()

			df = get_data(ticker)

			if len(df['open']) > 0 and len(df['volume']):
				avg_price = statistics.mean(df['open'])
				avg_volume = statistics.mean(df['volume'])
				if avg_price >= price_limit and avg_volume >= volume_limit:
					f.write('{}, avg price: {}, avg volume: {}\n'.format(ticker, avg_price, avg_volume))
					f.flush()
					close_open_plus_minus_bargraph(ticker, df)

def close_open_plus_minus_bargraph(ticker, df):

	ytemp = ((df['close'] - df['open'])/df['open']) * 100
	xtemp = range(1, len(ytemp)+ 1)

	x_above = []
	y_above = []
	x_below = []
	y_below = []

	i = 0
	while i < len(ytemp) - 1:
		close_open = (df['open'][i] - df['close'][i+1]) > 0
		if close_open:
			y_above.append(ytemp[i])
			x_above.append(xtemp[i])
		else:
			y_below.append(ytemp[i])
			x_below.append(xtemp[i])
		i += 1

	fig, ax = plt.subplots()

	plt.bar(x_above, y_above, color = 'Green')
	plt.bar(x_below, y_below, color = 'Red')
	plt.ylabel("percentage change")
	plt.xticks(xtemp,rotation = 90)

	above_mean = statistics.mean(y_above)
	below_mean = statistics.mean(y_below)
	
	ax.plot([0, 30], [above_mean, above_mean], 'k--')
	ax.plot([0, 30], [below_mean, below_mean], 'k--')

	plt.savefig('bargraph/{}.png'.format(ticker))

	plt.close()

def main():
	high_price_volume()

if __name__ == '__main__':
	main()
