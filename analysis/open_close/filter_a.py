# filter a:
# compiles a list of tickers that meet the following criteria:
# - price >= $100
# - volume >= 1000000
# - split close_open + and - and then find the mean gain and loss of each
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
# tentative = '../../tickers/tentative/{}.txt'.format('2022-06-22')
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

	open_close = ((df['close'] - df['open'])/df['open']) * 100
	x_values = range(1, len(open_close)+ 1)

	co_plus = {'y': [], 'x': [], 'oc+': [], 'x+': [], 'oc-': [], 'x-': [], 'count': 0}
	co_minus = {'y': [], 'x': [], 'oc+': [], 'x+': [], 'oc-': [], 'x-': [], 'count': 0}

	oc_plus = []
	oc_minus = []

	i = 0
	while i < len(open_close) - 1:
		# classifying based on whether close_open is positive or negative
		close_open = (df['open'][i] - df['close'][i+1]) > 0
		if close_open:
			co_plus['y'].append(open_close[i])
			co_plus['x'].append(x_values[i])
			# given co+, classify if oc is + or -
			co_plus['count'] += 1
			if open_close[i] > 0:
				co_plus['oc+'].append(open_close[i])
				co_plus['x+'].append(co_plus['count'])
				oc_plus.append(open_close[i])
			else:
				co_plus['oc-'].append(open_close[i])
				co_plus['x-'].append(co_plus['count'])
				oc_minus.append(open_close[i])
		else:
			co_minus['y'].append(open_close[i])
			co_minus['x'].append(x_values[i])
			# given co-, classify if oc is + or -
			co_minus['count'] += 1
			if open_close[i] > 0:
				co_minus['oc+'].append(open_close[i])
				co_minus['x+'].append(co_minus['count'])
				oc_plus.append(open_close[i])
			else:
				co_minus['oc-'].append(open_close[i])
				co_minus['x-'].append(co_minus['count'])
				oc_minus.append(open_close[i])

		i += 1

	fig, ax = plt.subplots(3, figsize=(10, 20))
	fig.tight_layout(pad=3)

	ax[0].bar(co_plus['x'], co_plus['y'], color = 'Green')
	ax[0].bar(co_minus['x'], co_minus['y'], color = 'Red')
	ax[0].set(title='Open Close +/-', xlabel='Days', ylabel='% Change')
	above_mean = statistics.mean(oc_plus)
	below_mean = statistics.mean(oc_minus)
	ax[0].plot([0, 30], [above_mean, above_mean], 'k--')
	ax[0].plot([0, 30], [below_mean, below_mean], 'k--')

	ax[1].bar(co_plus['x+'], co_plus['oc+'], color = 'Green')
	ax[1].bar(co_plus['x-'], co_plus['oc-'], color = 'Red')
	ax[1].set(title='Open Close +/- given CO +', xlabel='Days', ylabel='% Change')
	above_mean = statistics.mean(co_plus['oc+'])
	below_mean = statistics.mean(co_plus['oc-'])
	ax[1].plot([0, 30], [above_mean, above_mean], 'k--')
	ax[1].plot([0, 30], [below_mean, below_mean], 'k--')

	ax[2].bar(co_minus['x+'], co_minus['oc+'], color = 'Green')
	ax[2].bar(co_minus['x-'], co_minus['oc-'], color = 'Red')
	ax[2].set(title='Open Close +/- given CO -', xlabel='Days', ylabel='% Change')
	above_mean = statistics.mean(co_minus['oc+'])
	below_mean = statistics.mean(co_minus['oc-'])
	ax[2].plot([0, 30], [above_mean, above_mean], 'k--')
	ax[2].plot([0, 30], [below_mean, below_mean], 'k--')

	plt.savefig('bargraph/{}.png'.format(ticker))

	plt.close()


def main():
	high_price_volume()

if __name__ == '__main__':
	main()
