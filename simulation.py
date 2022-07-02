# run simulation and then graph it on matplotlib

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

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

today = datetime.now()
today_string = today.strftime('%Y-%m-%d')

cwd = os.getcwd()

simulation = os.path.join(cwd, 'simulation', '{}.txt'.format(today_string))
simulation_graph = os.path.join(cwd, 'simulation', '{}.png'.format(today_string))
ticker_list = os.path.join(cwd, 'tickers', 'tickers.txt')

price_limit = 50

sql = """
		SELECT * FROM daily 
		WHERE Ticker = 'AAPL'
	"""

totaldf = pd.read_sql(sql, engine)

rowcount = totaldf.shape[0]

# [ticker, plus/minus, deltagain, expected value, co strategy, today co, invest]
tentative_list = []
final = []

topindex = rowcount - 6
bottomindex = rowcount - 1

day_count = 1

def get_data(ticker):
	sql = """
			SELECT * FROM daily 
			WHERE Ticker = "{}"
			ORDER BY time DESC
		""".format(ticker)

	df = pd.read_sql(sql, engine)

	return df.iloc[topindex: bottomindex]

def high_price_volume():

	with open(ticker_list, 'r') as t:

		# for temp in t:
		for temp in ['AAPL']:
			ticker = temp.strip()

			try:
				df = get_data(ticker)

			except Exception as e:
				print('theres a problem', e)
				continue

			if len(df['open']):
				avg_price = statistics.mean(df['open'])
				if avg_price >= price_limit:
					close_open_filter(ticker, df)

def close_open_filter(ticker, df):

	try:

		y = ((df['close'] - df['open'])/df['open']) * 100
		avg = statistics.mean(y)
		if avg >= 0.5:
			tentative_list.append([ticker, avg])

	except:
		print('ERROR')
	
def rank_tentative():
	tentative_list.sort(key = lambda x: x[1], reverse = True)


def invest(money):

	rank_tentative()

	if money > 0:

		usable = money * .9
		reserve = money * .1
		split = [.5, .3, .2]
		gains = []
		results = []

		if len(tentative_list) > 3:
			i = 0
			while i < 3:
				ticker = tentative_list[i][0].strip()  
				temp = {'ticker': None, 'open': None, 'close': None, 'bought': None, 'sold': None, 'gain/loss': None}
				temp['ticker'] = ticker

				sql = """
				SELECT * FROM daily 
				WHERE Ticker = "{}"
				ORDER BY time DESC
				""".format(ticker)

				df = pd.read_sql(sql, engine)

				open_price = df['open'][topindex-1]
				close_price = df['close'][topindex-1]

				temp['open'] = open_price
				temp['close'] = close_price

				# qtybought = (usable * (1/3))  // open_price
				qtybought = (usable * split[i])  // open_price

				bought = qtybought * open_price
				sold = qtybought * close_price

				gainorloss = sold - bought

				gains.append(gainorloss)

				temp['bought'] = bought
				temp['sold'] = sold 
				temp['gain/loss'] = gainorloss

				results.append(temp)

				i += 1
		else:
			i = 0
			while i < len(tentative_list):
				ticker = tentative_list[i][0].strip()  
				temp = {'ticker': None, 'open': None, 'close': None, 'bought': None, 'sold': None, 'gain/loss': None}
				temp['ticker'] = ticker

				sql = """
				SELECT * FROM daily 
				WHERE Ticker = "{}"
				ORDER BY time DESC
				""".format(ticker)

				df = pd.read_sql(sql, engine)

				open_price = df['open'][topindex-1]
				close_price = df['close'][topindex-1]

				temp['open'] = open_price
				temp['close'] = close_price

				# qtybought = (usable * (1/3))  // open_price
				qtybought = (usable * split[i])  // open_price

				bought = qtybought * open_price
				sold = qtybought * close_price

				gainorloss = sold - bought

				gains.append(gainorloss)

				temp['bought'] = bought
				temp['sold'] = sold 
				temp['gain/loss'] = gainorloss

				results.append(temp)

				i += 1

		with open(simulation, 'a') as f:

			f.write('\nDay {}\n'.format(day_count))
			for item in results:
				f.write('{}, Open: {}, Close: {}, Bought: {}, Sold: {}, Gain/Loss: {}\n'.format(item['ticker'], item['open'], item['close'], item['bought'], item['sold'], item['gain/loss']))
				money += item['gain/loss']

			f.write('Total Gains/Losses: {}, Current Balance: {}\n'.format(sum(gains), money))

		return money

def run():

	global topindex, bottomindex, day_count, tentative_list, final

	balance_sheet = []
	initial = 10000
	money = initial
	balance_sheet.append(money)

	while topindex > 0:
		print('day', day_count)
		high_price_volume()
		temp = invest(money)
		print('invested')
		money = temp
		print('balance', money)
		balance_sheet.append(money)
		topindex -= 1
		bottomindex -= 1
		day_count += 1
		tentative_list = []
		final = []

	plt.plot(range(0, len(balance_sheet)), balance_sheet)
	plt.title('Gain for Open Close Method')
	plt.xlabel('Days')
	plt.ylabel('Balance')

	plt.savefig(simulation_graph)

	plt.close()

if __name__ == '__main__':
	run()
