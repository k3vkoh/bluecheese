# filter a:
# compiles a list of tickers that meet the following criteria:
# redo with 10 days and then 5 days then run the simulation
 

import pandas as pd 
from sqlalchemy.types import Text
from sqlalchemy import create_engine

import matplotlib
import matplotlib.pyplot as plt

import numpy as np
from scipy.stats import norm
import statistics

from datetime import datetime

import os
import requests
import glob

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

today = datetime.now()
today_string = today.strftime('%Y-%m-%d')

cwd = os.getcwd()

tentative = os.path.join(cwd, 'tickers/tentative', '{}.txt'.format(today_string))
ticker_list = os.path.join(cwd, 'tickers', 'tickers.txt')
bargraph = os.path.join(cwd, 'analysis/open_close/bargraph')

price_limit = 50

limit = 5

tentative_list = []

def get_data(ticker):
	sql = """
			SELECT * FROM daily 
			WHERE Ticker = "{}"
			ORDER BY time DESC
			LIMIT {}
		""".format(ticker, limit)

	df = pd.read_sql(sql, engine)

	return df

def price_filter():

	files = glob.glob(os.path.join(bargraph, '*'))
	for f in files:
		os.remove(f)

	with open(tentative, 'w') as f, open(ticker_list, 'r') as t:

		f.write('Filter: Price Filter\n')

		# for temp in ['AAPL']:
		for temp in t:
			ticker = temp.strip()

			df = get_data(ticker)

			if len(df['open']):
				avg_price = statistics.mean(df['open'])
				if avg_price >= price_limit:
					f.write('{}, avg price: {}\n'.format(ticker, avg_price))
					f.flush()
					calculate(ticker, df)

def calculate(ticker, df):

	# y is equal to open_close values
	y = ((df['close'] - df['open'])/df['open']) * 100
	x = range(0, len(y))

	avg = statistics.mean(y)

	# consecutive = [value < 0 for value in y]
	# if False not in consecutive:
	# 	tentative_list.append(ticker)

	if avg >= 0.5:
		tentative_list.append([ticker, avg])
	
	plt.plot(x, y)
	# plt.bar(positive['x'], positive['y'], color = 'Green')
	# plt.bar(negative['x'], negative['y'], color = 'Red')
	# plt.plot([0, len(x)-1], [high_avg, high_avg], 'g+')
	plt.plot([0, len(x)-1], [avg, avg], 'k--')
	# plt.plot([0, len(x)-1], [low_avg, low_avg], 'r-')

	plt.savefig(os.path.join(bargraph, '{}.png'.format(ticker)))

	plt.close()

def rank_tentative():
	tentative_list.sort(key = lambda x: x[1], reverse = True)

	with open(tentative, 'a') as f:

		f.write('\nFilter: Avg\n')
		for item in tentative_list:
			f.write('{}, Avg: {}\n'.format(item[0], item[1]))


def run():
	price_filter()
	rank_tentative()

