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

import analysis.open_close.filter_a as fila 

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

today = datetime.now()
today_string = today.strftime('%Y-%m-%d')

cwd = os.getcwd()

ticker_list = os.path.join(cwd, 'tickers', 'tickers.txt')
tentative = os.path.join(cwd, 'tickers/tentative', '{}.txt'.format(today_string))
bargraph = os.path.join(cwd, 'analysis/open_close/bargraph')

limit = 30

sql = """
		SELECT * FROM daily 
		WHERE Ticker = 'AAPL'
		ORDER BY time DESC
	"""

data = pd.read_sql(sql, engine)

rowcount = data.shape[0]

topindex = rowcount - 30
bottomindex = rowcount -1

def get_data(ticker):
	# sql = """
	# 		SELECT * FROM daily 
	# 		WHERE Ticker = "{}"
	# 		ORDER BY time DESC
	# 		LIMIT {}
	# 	""".format(ticker, limit)

	# df = pd.read_sql(sql, engine)

	# return df

	sql = """
			SELECT * FROM daily 
			WHERE Ticker = "{}"
			ORDER BY time DESC
		""".format(ticker)

	df = pd.read_sql(sql, engine)

	temp = df.copy(deep = True)

	df2 = temp.loc[topindex: bottomindex]

	df2.reset_index(inplace = True)

	return df2


def thumbsup():

	files = glob.glob(os.path.join(bargraph, '*'))
	for f in files:
		os.remove(f)

	final = []

	with open(ticker_list, 'r') as t:

		# for temp in ['AAPL']:
		for temp in t:

			ticker = temp.strip()

			try:
				df = get_data(ticker)
			except:
				continue

			if df.shape[0] != limit:
				continue

			tentative_list = fila.consecutive(ticker, df)
			filtered_list = fila.find_outliers(tentative_list)
			indicator = fila.indicator(filtered_list)
			thumbsup = fila.gogo(df, indicator)
			if thumbsup:
				final.append(ticker)

	return final

def main():

	global topindex, bottomindex

	plus_days = 0
	neg_days = 0
	day_count = 1

	balance_sheet = []
	initial = 10000
	money = initial
	balance_sheet.append(money)

	with open(tentative, 'w') as f:

		while topindex > 0:
			print('day', day_count)
			f.write('\nDay {}\n'.format(day_count))
			final = thumbsup()
			investable = money * .9
			for ticker in final:
				sql = """
						SELECT * FROM daily 
						WHERE Ticker = "{}"
						ORDER BY time DESC
					""".format(ticker)

				df = pd.read_sql(sql, engine)
				result = fila.invest(investable * (1/len(final)), ticker, df['open'][topindex-1],  df['close'][topindex-1])
				money += result['gain/loss']
				if result['gain/loss'] > 0:
					plus_days += 1
				elif result['gain/loss'] < 0:
					neg_days += 1
				f.write('{}, Open: {}, Close: {}, Bought: {}, Sold: {}, Gain/Loss: {}\n'.format(result['ticker'], result['open'], result['close'], result['bought'], result['sold'], result['gain/loss']))

			print('invested')
			print('balance', money)
			balance_sheet.append(money)
			topindex -= 1
			bottomindex -= 1
			day_count += 1

		print('net change', money - initial)
		print('high', max(balance_sheet))
		print('low', min(balance_sheet))
		try:
			print('positive days', plus_days/(plus_days + neg_days))
			print('negative days', neg_days/(plus_days + neg_days))
		except:
			pass
		f.write('Net Change: {}, Current Balance: {}\n'.format(money - initial, money))

		plt.plot(range(0, len(balance_sheet)), balance_sheet)
		plt.title('Gain for Open Close Method')
		plt.xlabel('Days')
		plt.ylabel('Balance')

		plt.savefig(os.path.join(bargraph, '{}.png'.format(today_string)))

		plt.close()


if __name__ == '__main__':
	main()



		

