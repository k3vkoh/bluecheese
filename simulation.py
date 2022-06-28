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

price_limit = 100
volume_limit = 500000
pmratio_limit = 1.5
deltagain_limit = 1.0

sql = """
		SELECT * FROM daily 
		WHERE Ticker = 'AAPL'
	"""

totaldf = pd.read_sql(sql, engine)

rowcount = totaldf.shape[0]

# [ticker, plus/minus, deltagain, expected value, co strategy, today co, invest]
tentative_list = []
final = []

topindex = rowcount - 31
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

		for temp in t:
			ticker = temp.strip()

			try:
				df = get_data(ticker)

			except Exception as e:
				print('theres a problem', e)
				continue

			if len(df['open']) and len(df['volume']):
				avg_price = statistics.mean(df['open'])
				avg_volume = statistics.mean(df['volume'])
				if avg_price >= price_limit and avg_volume >= volume_limit:
					close_open_filter(ticker, df)

def close_open_filter(ticker, df):

	open_close = ((df['close'] - df['open'])/df['open']) * 100

	co_plus = {'y': [], 'x': [], 'oc+': [], 'x+': [], 'oc-': [], 'x-': [], 'count': 0}
	co_minus = {'y': [], 'x': [], 'oc+': [], 'x+': [], 'oc-': [], 'x-': [], 'count': 0}

	i = topindex
	while i < bottomindex - 1:
		# classifying based on whether close_open is positive or negative
		close_open = (df['open'][i] - df['close'][i+1]) > 0
		if close_open:
			co_plus['y'].append(open_close[i])
			# given co+, classify if oc is + or -
			co_plus['count'] += 1
			if open_close[i] > 0:
				co_plus['oc+'].append(open_close[i])
				co_plus['x+'].append(co_plus['count'])
			else:
				co_plus['oc-'].append(open_close[i])
				co_plus['x-'].append(co_plus['count'])
		else:
			co_minus['y'].append(open_close[i])
			# given co-, classify if oc is + or -
			co_minus['count'] += 1
			if open_close[i] > 0:
				co_minus['oc+'].append(open_close[i])
				co_minus['x+'].append(co_minus['count'])
			else:
				co_minus['oc-'].append(open_close[i])
				co_minus['x-'].append(co_minus['count'])

		i += 1

	above_mean = statistics.mean(co_plus['oc+'])
	below_mean = statistics.mean(co_plus['oc-'])
	deltagain = above_mean - abs(below_mean)
	pmratio = len(co_plus['oc+']) / len(co_plus['oc-'])
	expectedvalue = ((len(co_plus['oc+'])/co_plus['count'])*above_mean) - ((len(co_plus['oc-'])/co_plus['count'])*abs(below_mean))
	if deltagain >= deltagain_limit and pmratio >= pmratio_limit:
		tentative_list.append([ticker, pmratio, deltagain, expectedvalue, '+', 0 ,None])

	above_mean = statistics.mean(co_minus['oc+'])
	below_mean = statistics.mean(co_minus['oc-'])
	deltagain = above_mean - abs(below_mean)
	pmratio = len(co_minus['oc+']) / len(co_minus['oc-'])
	expectedvalue = ((len(co_minus['oc+'])/co_minus['count'])*above_mean) - ((len(co_minus['oc-'])/co_minus['count'])*abs(below_mean))
	if deltagain >= deltagain_limit and pmratio >= pmratio_limit:
		tentative_list.append([ticker, pmratio, deltagain, expectedvalue, '-', 0, None])
	
def rank_tentative():
	# tentative_list.sort(key = lambda x: x[3], reverse = True)
	tentative_list.sort(key = lambda x: x[1], reverse = True)

def co_today():

	rank_tentative()

	for item in tentative_list:
		ticker = item[0]
		
		sql = """
			SELECT * FROM daily 
			WHERE Ticker = "{}"
			ORDER BY time DESC
			""".format(ticker)

		df = pd.read_sql(sql, engine)

		open_price = df['open'][topindex-1]
		close_price = df['close'][topindex]
		co = open_price - close_price
		item[5] = co
		if item[4] == '+':
			if co > 0:
				item[6] = 'Y'
			else:
				item[6] = 'N'
		elif item[4] == '-':
			if co < 0:
				item[6] = 'Y'
			else:
				item[6] = 'N'


def final_list():

	global final

	filtered = filter(lambda item: item[6] == 'Y', tentative_list)

	final = list(filtered)

def invest(money):

	if money > 0:

		# split #1 = 50%, #2 = 30%, #1 = 20%
		usable = money * .9
		reserve = money * .1
		split = [.5, .3, .2]
		gains = []
		results = []

		if len(final) > 3:
			i = 0
			while i < 3:
				ticker = final[i][0].strip()  
				temp = {'ticker': None, 'open': None, 'close': None, 'bought': None, 'sold': None, 'gain/loss': None, 'PMratio': None, 'Deltagain': None, 'Expected Value': None, 'CO Strategy': None, 'Today CO': None}
				temp['ticker'] = ticker
				temp['PMratio'] = final[i][1]
				temp['Deltagain'] = final[i][2]
				temp['Expected Value'] = final[i][3]
				temp['CO Strategy'] = final[i][4]
				temp['Today CO'] = final[i][5]

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

				qtybought = usable * split[i] // open_price

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
			while i < len(final):
				ticker = final[i][0].strip()  
				temp = {'ticker': None, 'open': None, 'close': None, 'bought': None, 'sold': None, 'gain/loss': None, 'PMratio': None, 'Deltagain': None, 'Expected Value': None, 'CO Strategy': None, 'Today CO': None}
				temp['ticker'] = ticker
				temp['PMratio'] = final[i][1]
				temp['Deltagain'] = final[i][2]
				temp['Expected Value'] = final[i][3]
				temp['CO Strategy'] = final[i][4]
				temp['Today CO'] = final[i][5]

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

				qtybought = usable * split[i] // open_price

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
				f.write('{}, Open: {}, Close: {}, Bought: {}, Sold: {}, Gain/Loss: {}, PMratio: {}, Deltagain: {}, Expected Value: {}, CO Strategy: {}, Today CO: {}\n'.format(item['ticker'], item['open'], item['close'], item['bought'], item['sold'], item['gain/loss'], item['PMratio'], item['Deltagain'], item['Expected Value'], item['CO Strategy'], item['Today CO']))
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
		co_today()
		final_list()
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
