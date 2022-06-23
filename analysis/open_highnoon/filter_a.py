# filter a:
# compiles a list of tickers that meet the following criteria:
# 	- based on the tickers from filter a, now see the noon prices and open prices
#   - also analyse the premarket

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

limit = 30
constant = limit * 16

tentative_list = []

def get_data_hourly(ticker):
	sql = """
			SELECT * FROM hourly 
			WHERE Ticker = "{}"
			ORDER BY time DESC
			LIMIT {}
		""".format(ticker, constant)

	df = pd.read_sql(sql, engine)

	return df

def get_data_daily(ticker):
	sql = """
			SELECT * FROM daily 
			WHERE Ticker = "{}"
			ORDER BY time DESC
			LIMIT {}
		""".format(ticker, limit)

	df = pd.read_sql(sql, engine)

	return df

def open_noon_price():

	with open(tentative, 'r') as t:

		for temp in t:

			temp_list = temp.split(',')
			ticker = temp_list[0].strip()

			df_hourly = get_data_hourly(ticker)
			df_daily = get_data_daily(ticker)

			noon_times = ['12:00:00' in x for x in df_hourly['date']]
			noon_prices = df_hourly['open'][noon_times].tolist()
			open_prices = df_daily['open'].tolist()

			noon_open = list()

			for noon_prices, open_prices in zip(noon_prices, open_prices):
				noon_open.append(((noon_prices - open_prices)/open_prices) * 100)
			
			# open_close_plus_minus_bargraph(ticker, noon_open)
			close_open_plus_minus_bargraph(ticker, noon_open, df_daily)


def open_close_plus_minus_bargraph(ticker, data):

	xtemp = range(1, len(data)+ 1)

	x_above = []
	y_above = []
	x_below = []
	y_below = []

	i = 0
	while i < len(data):
		if data[i] > 0:
			y_above.append(ytemp[i])
			x_above.append(xtemp[i])
		else:
			y_below.append(ytemp[i])
			x_below.append(xtemp[i])
		i += 1

	fig, ax = plt.subplots()

	plt.bar(x_above, y_above)
	plt.bar(x_below, y_below)
	plt.ylabel("percentage change")
	plt.xticks(xtemp,rotation = 90)

	above_mean = statistics.mean(y_above)
	below_mean = statistics.mean(y_below)
	
	ax.plot([0, 30], [above_mean, above_mean], 'k--')
	ax.plot([0, 30], [below_mean, below_mean], 'k--')

	plt.savefig('bargraph/{}_b.png'.format(ticker))

	plt.close()


def close_open_plus_minus_bargraph(ticker, data, df):

	xtemp = range(1, len(data)+ 1)

	x_above = []
	y_above = []
	x_below = []
	y_below = []

	i = 0
	while i < len(data) - 1:
		close_open = (df['open'][i] - df['close'][i+1]) > 0
		if close_open:
			y_above.append(data[i])
			x_above.append(xtemp[i])
		else:
			y_below.append(data[i])
			x_below.append(xtemp[i])
		i += 1

	fig, ax = plt.subplots()

	plt.bar(x_above, y_above, color = 'Green')
	plt.bar(x_below, y_below, color = 'Red')
	plt.ylabel("percentage change")
	plt.xticks(xtemp,rotation = 90)

	plt.savefig('bargraph/{}_b.png'.format(ticker))

	plt.close()

def main():
	open_noon_price()

if __name__ == '__main__':
	main()
