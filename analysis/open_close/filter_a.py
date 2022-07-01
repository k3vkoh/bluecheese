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
# volume_limit = 500000
# pmratio_limit = 2.0
# deltagain_limit = 0.5

limit = 5

# [ticker, plus/minus, deltagain, expected value]
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

def find_outliers(data):
	dataset = sorted(data)
	q1, q3 = np.percentile(dataset,[25,75])
	iqr = q3 - q1
	upper = q3 + (1.5 * iqr)
	lower = q1 - (1.5 * iqr)
	return [x >= lower and x <= upper for x in data]

def calculate(ticker, df):

	# y is equal to open_close values
	y_initial = ((df['close'] - df['open'])/df['open']) * 100
	y = y_initial[find_outliers(y_initial)]
	x = np.arange(0, len(y))
	A = np.array([x, np.ones(len(x))])
	results = np.linalg.lstsq(A.T, y, rcond=None)
	w = results[0]
	r2 = results[1]

	if w[0] > 0 and r2 < 10:
		tentative_list.append([ticker, w[0], r2])

	# regression line
	line = w[0]*x + w[1]  
	plt.plot(x, line, 'r-')
	plt.plot(x, y, 'o')

	plt.savefig(os.path.join(bargraph, '{}.png'.format(ticker)))

	plt.close()

def rank_tentative():
	tentative_list.sort(key = lambda x: x[1], reverse = True)

	with open(tentative, 'a') as f:

		f.write('\nFilter: Slope and R2\n')
		for item in tentative_list:
			f.write('{}, Slope: {}, Sum of R2: {}\n'.format(item[0], item[1], item[2]))


def run():
	price_filter()
	rank_tentative()

