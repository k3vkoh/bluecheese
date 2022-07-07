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
import glob

import analysis.open_close.filter_a as fila 

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

today = datetime.now()
today_string = today.strftime('%Y-%m-%d')

cwd = os.getcwd()

ticker_list = os.path.join(cwd, 'tickers', 'tickers.txt')
tentative = os.path.join(cwd, 'tickers/tentative', '{}.txt'.format(today_string))
bargraph = os.path.join(cwd, 'analysis/open_close/bargraph')

# when getting data for all days
# sql = """
# 		SELECT * FROM daily 
# 		WHERE Ticker = 'AAPL'
# 	"""

# totaldf = pd.read_sql(sql, engine)

# rowcount = totaldf.shape[0]

# when getting data for limit days
limit = 30

def get_data(ticker):
	# when doing all data
	# sql = """
	# 		SELECT * FROM daily 
	# 		WHERE Ticker = "{}"
	# 		ORDER BY time DESC
	# 	""".format(ticker)

	# when getting only limit number of days
	sql = """
			SELECT * FROM daily 
			WHERE Ticker = "{}"
			ORDER BY time DESC
			LIMIT {}
		""".format(ticker, limit)

	df = pd.read_sql(sql, engine)

	return df


def main():

	files = glob.glob(os.path.join(bargraph, '*'))
	for f in files:
		os.remove(f)

	with open(ticker_list, 'r') as t, open(tentative, 'w') as f:

		for temp in ['AAPL']:
		# for temp in t:

			ticker = temp.strip()

			df = get_data(ticker)

			if df.shape[0] != limit:
				continue

			tentative_list = fila.consecutive(ticker, df)
			filtered_list = fila.find_outliers(tentative_list)
			indicator = fila.indicator(filtered_list)
			thumbsup = fila.gogo(df, indicator)
			print(thumbsup)

			# f.write("{}\n".format(ticker))
			# for x in filtered_list:
			# 	f.write('{} {} consecutive days\n'.format(x[2], x[1]))

			# neg = list(filter(lambda x: x[1] == '-', filtered_list))
			# pos = list(filter(lambda x: x[1] == '+', filtered_list))

			# neg_num_list = [x[2] for x in neg]
			# pos_num_list = [x[2] for x in pos]
			# total = [x[2] for x in filtered_list]

			# neg_avg = statistics.mean(neg_num_list)
			# pos_avg = statistics.mean(pos_num_list)

			# f.write('avg consecutive - days: {}\n'.format(neg_avg))
			# f.write('avg consecutive + days: {}\n'.format(pos_avg))
			# f.write('total days: {}\n'.format(sum(total)))

if __name__ == '__main__':
	main()


# def invest(money):

# 	rank_tentative()

# 	global plus_days, neg_days

# 	if money > 0:

# 		usable = money * .9
# 		reserve = money * .1
# 		split = [.5, .3, .2]
# 		gains = []
# 		results = []

# 		if len(tentative_list) > 3:
# 			i = 0
# 			while i < 3:
# 				ticker = tentative_list[i][0].strip()  
# 				temp = {'ticker': None, 'open': None, 'close': None, 'bought': None, 'sold': None, 'gain/loss': None}
# 				temp['ticker'] = ticker

# 				sql = """
# 				SELECT * FROM daily 
# 				WHERE Ticker = "{}"
# 				ORDER BY time DESC
# 				""".format(ticker)

# 				df = pd.read_sql(sql, engine)

# 				open_price = df['open'][topindex-1]
# 				close_price = df['close'][topindex-1]

# 				temp['open'] = open_price
# 				temp['close'] = close_price

# 				# qtybought = (usable * (1/3))  // open_price
# 				qtybought = (usable * split[i])  // open_price

# 				bought = qtybought * open_price
# 				sold = qtybought * close_price

# 				gainorloss = sold - bought

# 				if gainorloss > 0:
# 					plus_days += 1
# 				else:
# 					neg_days += 1

# 				gains.append(gainorloss)

# 				temp['bought'] = bought
# 				temp['sold'] = sold 
# 				temp['gain/loss'] = gainorloss

# 				results.append(temp)

# 				i += 1
# 		else:
# 			i = 0
# 			while i < len(tentative_list):
# 				ticker = tentative_list[i][0].strip()  
# 				temp = {'ticker': None, 'open': None, 'close': None, 'bought': None, 'sold': None, 'gain/loss': None}
# 				temp['ticker'] = ticker

# 				sql = """
# 				SELECT * FROM daily 
# 				WHERE Ticker = "{}"
# 				ORDER BY time DESC
# 				""".format(ticker)

# 				df = pd.read_sql(sql, engine)

# 				open_price = df['open'][topindex-1]
# 				close_price = df['close'][topindex-1]

# 				temp['open'] = open_price
# 				temp['close'] = close_price

# 				# qtybought = (usable * (1/3))  // open_price
# 				qtybought = (usable * split[i])  // open_price

# 				bought = qtybought * open_price
# 				sold = qtybought * close_price

# 				gainorloss = sold - bought

# 				if gainorloss > 0:
# 					plus_days += 1
# 				else:
# 					neg_days += 1

# 				gains.append(gainorloss)

# 				temp['bought'] = bought
# 				temp['sold'] = sold 
# 				temp['gain/loss'] = gainorloss

# 				results.append(temp)

# 				i += 1

# 		with open(simulation, 'w') as f:

# 			f.write('\nDay {}\n'.format(day_count))
# 			for item in results:
# 				f.write('{}, Open: {}, Close: {}, Bought: {}, Sold: {}, Gain/Loss: {}\n'.format(item['ticker'], item['open'], item['close'], item['bought'], item['sold'], item['gain/loss']))
# 				money += item['gain/loss']

# 			f.write('Total Gains/Losses: {}, Current Balance: {}\n'.format(sum(gains), money))

# 		return money

# def run():

# 	global topindex, bottomindex, day_count, tentative_list

# 	balance_sheet = []
# 	initial = 10000
# 	money = initial
# 	balance_sheet.append(money)

# 	while topindex > 0:
# 		print('day', day_count)
# 		high_price_volume()
# 		temp = invest(money)
# 		print('invested')
# 		money = temp
# 		print('balance', money)
# 		balance_sheet.append(money)
# 		topindex -= 1
# 		bottomindex -= 1
# 		day_count += 1
# 		tentative_list = []

# 	print('net change', money - initial)
# 	print('high', max(balance_sheet))
# 	print('low', min(balance_sheet))
# 	print('positive days', plus_days/(plus_days + neg_days))
# 	print('negative days', neg_days/(plus_days + neg_days))


# 	plt.plot(range(0, len(balance_sheet)), balance_sheet)
# 	plt.title('Gain for Open Close Method')
# 	plt.xlabel('Days')
# 	plt.ylabel('Balance')

# 	plt.savefig(simulation_graph)

# 	plt.close()

# if __name__ == '__main__':
# 	run()


