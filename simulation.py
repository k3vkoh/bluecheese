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
tentative = os.path.join(cwd, 'results', '{}.txt'.format(today_string))
bargraph = os.path.join(cwd, 'results', '{}.png'.format(today_string))

limit = 30

sql = """
		SELECT * FROM daily 
		WHERE Ticker = 'AAPL'
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
			ORDER BY Date DESC
		""".format(ticker)

	df = pd.read_sql(sql, engine)

	temp = df.copy(deep = True)

	df2 = temp.loc[topindex: bottomindex]

	df2.reset_index(inplace = True)

	return df2


def thumbsup():

	final = []

	with open(ticker_list, 'r') as t:

		# for temp in ['AAPL']:
		for temp in ['AAPL', 'AMZN', 'TSLA', 'MSFT', 'ABNB']:
		# for temp in t:

			ticker = temp.strip()

			try:
				df = get_data(ticker)
			except:
				print('error')
				continue

			if df.shape[0] != limit:
				continue

			result = fila.gogo(df)
			count = result[0]
			mode = result[1]

			if mode == 'minus' and count >= 4:
				final.append([ticker, mode, count])

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
			f.flush()
			final = thumbsup()
			investable = money * .9
			totalgain = 0
			for value in final:
				ticker = value[0]
				mode = value[1]
				count = value[2]
				sql = """
						SELECT * FROM daily 
						WHERE Ticker = "{}"
						ORDER BY Date DESC
					""".format(ticker)

				df = pd.read_sql(sql, engine)
				result = fila.invest(investable * (1/len(final)), ticker, df['Open'][topindex-1],  df['Close'][topindex-1], mode, count)
				totalgain += result['gain/loss']
				f.write('{}, Open: {}, Close: {}, Bought: {}, Sold: {}, Gain/Loss: {}, Mode: {}, Count: {}\n'.format(result['ticker'], result['open'], result['close'], result['bought'], result['sold'], result['gain/loss'], result['mode'], result['count']))
				f.flush()

			money += totalgain
			if totalgain > 0:
				plus_days += 1
			elif totalgain < 0:
				neg_days += 1
			print('invested')
			f.write('current balance: {}\n'.format(money))
			print('balance', money)
			balance_sheet.append(money)
			topindex -= 1
			bottomindex -= 1
			day_count += 1

		print('net change', money - initial)
		print('high', max(balance_sheet))
		print('low', min(balance_sheet))
		# print('positive days', plus_days/(plus_days + neg_days))
		# print('negative days', neg_days/(plus_days + neg_days))
		print('positive days', plus_days)
		print('negative days', neg_days)
		f.write('Net Change: {}, Current Balance: {}\n'.format(money - initial, money))
		f.flush()

		plt.plot(range(0, len(balance_sheet)), balance_sheet)
		plt.title('Gain for Open Close Method')
		plt.xlabel('Days')
		plt.ylabel('Balance')

		plt.savefig(bargraph)

		plt.close()


if __name__ == '__main__':
	main()



		

