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


# # run simulation and then graph it on matplotlib
# open high based on close open

# import pandas as pd 
# from sqlalchemy.types import Text
# from sqlalchemy import create_engine

# import matplotlib
# import matplotlib.pyplot as plt

# import numpy as np
# from scipy.stats import norm
# import statistics

# from datetime import datetime

# import os
# import requests

# engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

# today = datetime.now()
# today_string = today.strftime('%Y-%m-%d')

# cwd = os.getcwd()

# simulation = os.path.join(cwd, 'simulation', '{}.txt'.format(today_string))
# simulation_graph = os.path.join(cwd, 'simulation', '{}.png'.format(today_string))
# ticker_list = os.path.join(cwd, 'tickers', 'tickers.txt')

# price_limit = 50
# volume_limit = 500000
# high_limit = 2.5

# sql = """
# 		SELECT * FROM daily 
# 		WHERE Ticker = 'AAPL'
# 	"""

# totaldf = pd.read_sql(sql, engine)

# rowcount = totaldf.shape[0]

# # [ticker, high avg, co strategy, today co, invest]
# tentative_list = []
# final = []

# topindex = rowcount - 5
# bottomindex = rowcount - 1

# day_count = 1

# def get_data(ticker):
# 	sql = """
# 			SELECT * FROM daily 
# 			WHERE Ticker = "{}"
# 			ORDER BY time DESC
# 		""".format(ticker)

# 	df = pd.read_sql(sql, engine)

# 	return df.iloc[topindex: bottomindex]

# def high_price_volume():

# 	with open(ticker_list, 'r') as t:

# 		for temp in t:
# 			ticker = temp.strip()

# 			try:
# 				df = get_data(ticker)

# 			except Exception as e:
# 				print('theres a problem', e)
# 				continue

# 			if len(df['open']) and len(df['volume']):
# 				avg_price = statistics.mean(df['open'])
# 				avg_volume = statistics.mean(df['volume'])
# 				if avg_price >= price_limit and avg_volume >= volume_limit:
# 					close_open_filter(ticker, df)

# def close_open_filter(ticker, df):

# 	try:
# 		open_high = ((df['high'] - df['open'])/df['open']) * 100
# 		avg_high = statistics.mean(open_high)

# 		if avg_high >= high_limit:
# 			tentative_list.append([ticker, avg_high])
# 	except:
# 		print(ticker)
# 		print('ERROR')
	
# def rank_tentative():
# 	tentative_list.sort(key = lambda x: x[1], reverse = True)

# def invest(money):

# 	rank_tentative()

# 	if money > 0:

# 		usable = money * .9
# 		reserve = money * .1
# 		split = [.5, .3, .2]
# 		gains = []
# 		results = []

# 		# if len(tentative_list) > 5:
# 		# 	i = 0
# 		# 	while i < 5:
# 		# 		ticker = tentative_list[i][0].strip()  
# 		# 		temp = {'ticker': None, 'open': None, 'high': None, 'close': None,'sell': None, 'bought': None, 'sold': None, 'gain/loss': None, 'average high': None}
# 		# 		temp['ticker'] = ticker
# 		# 		temp['average high'] = tentative_list[i][1]

# 		# 		sql = """
# 		# 		SELECT * FROM daily 
# 		# 		WHERE Ticker = "{}"
# 		# 		ORDER BY time DESC
# 		# 		""".format(ticker)

# 		# 		df = pd.read_sql(sql, engine)

# 		# 		open_price = df['open'][topindex-1]
# 		# 		high_price = df['high'][topindex-1]
# 		# 		close_price = df['close'][topindex-1]
# 		# 		sell_price = (1 + ((tentative_list[i][1]/100)/2)) * open_price
# 		# 		# sell_price = (1 + ((high_limit/100)/2)) * open_price

# 		# 		temp['open'] = open_price
# 		# 		temp['high'] = high_price
# 		# 		temp['close'] = close_price
# 		# 		temp['sell'] = sell_price

# 		# 		qtybought = (usable * (1/len(tentative_list)))  // open_price
# 		# 		# qtybought = (usable * split[i])  // open_price

# 		# 		bought = qtybought * open_price

# 		# 		sold = 0
# 		# 		if high_price > sell_price:
# 		# 			sold = qtybought * sell_price
# 		# 			print('sold via sell price')
# 		# 		else: 
# 		# 			sold = qtybought * close_price
# 		# 			print('sold via close price')

# 		# 		gainorloss = sold - bought

# 		# 		gains.append(gainorloss)

# 		# 		temp['bought'] = bought
# 		# 		temp['sold'] = sold 
# 		# 		temp['gain/loss'] = gainorloss

# 		# 		results.append(temp)

# 		# 		i += 1
# 		# else:
# 		i = 0
# 		while i < len(tentative_list):
# 			ticker = tentative_list[i][0].strip()  
# 			temp = {'ticker': None, 'open': None, 'high': None, 'close': None,'sell': None, 'bought': None, 'sold': None, 'gain/loss': None, 'average high': None}
# 			temp['ticker'] = ticker
# 			temp['average high'] = tentative_list[i][1]

# 			sql = """
# 			SELECT * FROM daily 
# 			WHERE Ticker = "{}"
# 			ORDER BY time DESC
# 			""".format(ticker)

# 			df = pd.read_sql(sql, engine)

# 			open_price = df['open'][topindex-1]
# 			high_price = df['high'][topindex-1]
# 			close_price = df['close'][topindex-1]
# 			sell_price = 1.0025 * open_price
# 			# sell_price = (1 + ((tentative_list[i][1]/100)/2)) * open_price
# 			# sell_price = (1 + ((high_limit/100)/2)) * open_price

# 			temp['open'] = open_price
# 			temp['high'] = high_price
# 			temp['close'] = close_price
# 			temp['sell'] = sell_price

# 			qtybought = (usable * (1/len(tentative_list)))  // open_price
# 			# qtybought = (usable * split[i])  // open_price

# 			bought = qtybought * open_price

# 			sold = 0
# 			if high_price > sell_price:
# 				sold = qtybought * sell_price
# 				print('sold via sell price')
# 			else: 
# 				sold = qtybought * close_price
# 				print('sold via close price')

# 			gainorloss = sold - bought

# 			gains.append(gainorloss)

# 			temp['bought'] = bought
# 			temp['sold'] = sold 
# 			temp['gain/loss'] = gainorloss

# 			results.append(temp)

# 			i += 1

# 		with open(simulation, 'a') as f:

# 			f.write('\nDay {}\n'.format(day_count))
# 			for item in results:
# 				f.write('{}, Open: {}, High: {}, Close: {}, Sell: {}, Bought: {}, Sold: {}, Gain/Loss: {}, Average High: {}\n'.format(item['ticker'], item['open'], item['high'], item['close'], item['sell'], item['bought'], item['sold'], item['gain/loss'], item['average high']))
# 				money += item['gain/loss']

# 			f.write('Total Gains/Losses: {}, Current Balance: {}\n'.format(sum(gains), money))

# 		return money

# def run():

# 	global topindex, bottomindex, day_count, tentative_list, final

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
# 		final = []

# 	print('max', max(balance_sheet))
# 	print('min', min(balance_sheet))
# 	print('change', money - initial)
# 	plt.plot(range(0, len(balance_sheet)), balance_sheet)
# 	plt.title('Gain for Open Close Method')
# 	plt.xlabel('Days')
# 	plt.ylabel('Balance')

# 	plt.savefig(simulation_graph)

# 	plt.close()

# if __name__ == '__main__':
# 	run()




# # run simulation and then graph it on matplotlib
# open high based on top 5 avg

# import pandas as pd 
# from sqlalchemy.types import Text
# from sqlalchemy import create_engine

# import matplotlib
# import matplotlib.pyplot as plt

# import numpy as np
# from scipy.stats import norm
# import statistics

# from datetime import datetime

# import os
# import requests

# engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

# today = datetime.now()
# today_string = today.strftime('%Y-%m-%d')

# cwd = os.getcwd()

# simulation = os.path.join(cwd, 'simulation', '{}.txt'.format(today_string))
# simulation_graph = os.path.join(cwd, 'simulation', '{}.png'.format(today_string))
# ticker_list = os.path.join(cwd, 'tickers', 'tickers.txt')

# price_limit = 50
# volume_limit = 500000
# high_limit = 4
# high_len_limit = 4

# sql = """
# 		SELECT * FROM daily 
# 		WHERE Ticker = 'AAPL'
# 	"""

# totaldf = pd.read_sql(sql, engine)

# rowcount = totaldf.shape[0]

# # [ticker, high avg, co strategy, today co, invest]
# tentative_list = []
# final = []

# topindex = rowcount - 10
# bottomindex = rowcount - 1

# day_count = 1

# def get_data(ticker):
# 	sql = """
# 			SELECT * FROM daily 
# 			WHERE Ticker = "{}"
# 			ORDER BY time DESC
# 		""".format(ticker)

# 	df = pd.read_sql(sql, engine)

# 	return df.iloc[topindex: bottomindex]

# def high_price_volume():

# 	with open(ticker_list, 'r') as t:

# 		for temp in t:
# 			ticker = temp.strip()

# 			try:
# 				df = get_data(ticker)

# 			except Exception as e:
# 				print('theres a problem', e)
# 				continue

# 			if len(df['open']) and len(df['volume']):
# 				avg_price = statistics.mean(df['open'])
# 				avg_volume = statistics.mean(df['volume'])
# 				if avg_price >= price_limit and avg_volume >= volume_limit:
# 					close_open_filter(ticker, df)

# def close_open_filter(ticker, df):

# 	try:
# 		open_high = ((df['high'] - df['open'])/df['open']) * 100

# 		co_plus = {'y': [], 'x': [], 'count': 0}
# 		co_minus = {'y': [], 'x': [], 'count': 0}

# 		i = topindex
# 		while i < bottomindex - 1:
# 			# classifying based on whether close_open is positive or negative
# 			close_open = (df['open'][i] - df['close'][i+1]) > 0
# 			if close_open:
# 				co_plus['y'].append(open_high[i])
# 				# given co+, classify if oc is + or -
# 				co_plus['count'] += 1
# 			else:
# 				co_minus['y'].append(open_high[i])
# 				# given co-, classify if oc is + or -
# 				co_minus['count'] += 1

# 			i += 1

# 		high_avg = statistics.mean(co_plus['y'])
# 		if high_avg >= high_limit and len(co_plus['y']) >= high_len_limit:
# 			tentative_list.append([ticker, high_avg, '+', 0 ,None])

# 		high_avg = statistics.mean(co_minus['y'])
# 		if high_avg >= high_limit and len(co_minus['y']) >= high_len_limit:
# 			tentative_list.append([ticker, high_avg, '-', 0, None])
# 	except:
# 		print(ticker)
# 		print('ERROR')
	
# def rank_tentative():
# 	tentative_list.sort(key = lambda x: x[1], reverse = True)

# def co_today():

# 	rank_tentative()

# 	for item in tentative_list:
# 		ticker = item[0]
		
# 		sql = """
# 			SELECT * FROM daily 
# 			WHERE Ticker = "{}"
# 			ORDER BY time DESC
# 			""".format(ticker)

# 		df = pd.read_sql(sql, engine)

# 		open_price = df['open'][topindex-1]
# 		close_price = df['close'][topindex]
# 		co = open_price - close_price
# 		item[3] = co
# 		if item[2] == '+':
# 			if co > 0:
# 				item[4] = 'Y'
# 			else:
# 				item[4] = 'N'
# 		elif item[2] == '-':
# 			if co < 0:
# 				item[4] = 'Y'
# 			else:
# 				item[4] = 'N'


# def final_list():

# 	global final

# 	filtered = filter(lambda item: item[4] == 'Y', tentative_list)

# 	final = list(filtered)

# def invest(money):

# 	if money > 0:

# 		usable = money * .9
# 		reserve = money * .1
# 		split = [.5, .3, .2]
# 		gains = []
# 		results = []

# 		if len(final) > 3:
# 			i = 0
# 			while i < 3:
# 				ticker = final[i][0].strip()  
# 				temp = {'ticker': None, 'open': None, 'high': None, 'close': None,'sell': None, 'bought': None, 'sold': None, 'gain/loss': None, 'average high': None, 'CO Strategy': None, 'Today CO': None}
# 				temp['ticker'] = ticker
# 				temp['average high'] = final[i][1]
# 				temp['CO Strategy'] = final[i][2]
# 				temp['Today CO'] = final[i][3]

# 				sql = """
# 				SELECT * FROM daily 
# 				WHERE Ticker = "{}"
# 				ORDER BY time DESC
# 				""".format(ticker)

# 				df = pd.read_sql(sql, engine)

# 				open_price = df['open'][topindex-1]
# 				high_price = df['high'][topindex-1]
# 				close_price = df['close'][topindex-1]
# 				# sell_price = (1 + ((final[i][1]/100)/2)) * open_price
# 				sell_price = (1 + ((high_limit/100)/2)) * open_price

# 				temp['open'] = open_price
# 				temp['high'] = high_price
# 				temp['close'] = close_price
# 				temp['sell'] = sell_price

# 				# qtybought = (usable * (1/3))  // open_price
# 				qtybought = (usable * split[i])  // open_price

# 				bought = qtybought * open_price

# 				sold = 0
# 				if high_price > sell_price:
# 					sold = qtybought * sell_price
# 					print('sold via sell price')
# 				else: 
# 					sold = qtybought * close_price
# 					print('sold via close price')

# 				gainorloss = sold - bought

# 				gains.append(gainorloss)

# 				temp['bought'] = bought
# 				temp['sold'] = sold 
# 				temp['gain/loss'] = gainorloss

# 				results.append(temp)

# 				i += 1
# 		else:
# 			i = 0
# 			while i < len(final):
# 				ticker = final[i][0].strip()  
# 				temp = {'ticker': None, 'open': None, 'high': None, 'close': None,'sell': None, 'bought': None, 'sold': None, 'gain/loss': None, 'average high': None, 'CO Strategy': None, 'Today CO': None}
# 				temp['ticker'] = ticker
# 				temp['average high'] = final[i][1]
# 				temp['CO Strategy'] = final[i][2]
# 				temp['Today CO'] = final[i][3]

# 				sql = """
# 				SELECT * FROM daily 
# 				WHERE Ticker = "{}"
# 				ORDER BY time DESC
# 				""".format(ticker)

# 				df = pd.read_sql(sql, engine)

# 				open_price = df['open'][topindex-1]
# 				high_price = df['high'][topindex-1]
# 				close_price = df['close'][topindex-1]
# 				# sell_price = (1 + ((final[i][1]/100)/2)) * open_price
# 				sell_price = (1 + ((high_limit/100)/2)) * open_price

# 				temp['open'] = open_price
# 				temp['high'] = high_price
# 				temp['close'] = close_price
# 				temp['sell'] = sell_price

# 				# qtybought = (usable * (1/3))  // open_price
# 				qtybought = (usable * split[i])  // open_price

# 				bought = qtybought * open_price

# 				sold = 0
# 				if high_price > sell_price:
# 					sold = qtybought * sell_price
# 					print('sold via sell price')
# 				else: 
# 					sold = qtybought * close_price
# 					print('sold via close price')

# 				gainorloss = sold - bought

# 				gains.append(gainorloss)

# 				temp['bought'] = bought
# 				temp['sold'] = sold 
# 				temp['gain/loss'] = gainorloss

# 				results.append(temp)

# 				i += 1

# 		with open(simulation, 'a') as f:

# 			f.write('\nDay {}\n'.format(day_count))
# 			for item in results:
# 				f.write('{}, Open: {}, High: {}, Close: {}, Sell: {}, Bought: {}, Sold: {}, Gain/Loss: {}, Average High: {}, CO Strategy: {}, Today CO: {}\n'.format(item['ticker'], item['open'], item['high'], item['close'], item['sell'], item['bought'], item['sold'], item['gain/loss'], item['average high'], item['CO Strategy'], item['Today CO']))
# 				money += item['gain/loss']

# 			f.write('Total Gains/Losses: {}, Current Balance: {}\n'.format(sum(gains), money))

# 		return money

# def run():

# 	global topindex, bottomindex, day_count, tentative_list, final

# 	balance_sheet = []
# 	initial = 10000
# 	money = initial
# 	balance_sheet.append(money)

# 	while topindex > 0:
# 		print('day', day_count)
# 		high_price_volume()
# 		co_today()
# 		final_list()
# 		temp = invest(money)
# 		print('invested')
# 		money = temp
# 		print('balance', money)
# 		balance_sheet.append(money)
# 		topindex -= 1
# 		bottomindex -= 1
# 		day_count += 1
# 		tentative_list = []
# 		final = []

# 	plt.plot(range(0, len(balance_sheet)), balance_sheet)
# 	plt.title('Gain for Open Close Method')
# 	plt.xlabel('Days')
# 	plt.ylabel('Balance')

# 	plt.savefig(simulation_graph)

# 	plt.close()

# if __name__ == '__main__':
# 	run()


