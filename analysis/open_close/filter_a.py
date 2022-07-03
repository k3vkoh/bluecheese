# filter a:
# compiles a list of tickers that meet the following criteria:
 
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

sql = """
		SELECT * FROM daily 
		WHERE Ticker = 'AAPL'
	"""

totaldf = pd.read_sql(sql, engine)

rowcount = totaldf.shape[0]

def get_data(ticker):
	sql = """
			SELECT * FROM daily 
			WHERE Ticker = "{}"
			ORDER BY time DESC
		""".format(ticker)

	df = pd.read_sql(sql, engine)

	return df

def consecutive():

	files = glob.glob(os.path.join(bargraph, '*'))
	for f in files:
		os.remove(f)

	with open(tentative, 'w') as f, open(ticker_list, 'r') as t:

		# for temp in ['AAPL']:
		for temp in t:

			tentative_list = [] 

			ticker = temp.strip()

			df = get_data(ticker)

			if df.shape[0] != rowcount:
				continue

			open_close = df['close'] - df['open']

			pd.set_option('display.max_rows', None)

			i = rowcount - 1
			while i > 0:
				consecutive_neg = 0
				consecutive_pos = 0
				sign_change = False
				while not sign_change and i > 0:
					if open_close[i] > 0:
						consecutive_pos += 1
					else:
						consecutive_neg += 1
					today = open_close[i] > 0
					tomorrow = open_close[i-1] > 0
					if today != tomorrow:
						sign_change = True
						if consecutive_pos:
							tentative_list.append([ticker, '+', consecutive_pos])
						else:
							tentative_list.append([ticker, '-', consecutive_neg])
					else:
						i -= 1
						if i == 0:
							if consecutive_pos:
								tentative_list.append([ticker, '+', consecutive_pos])
							else:
								tentative_list.append([ticker, '-', consecutive_neg])
				i -= 1

			f.write("{}\n".format(ticker))
			for x in tentative_list:
				f.write('{} {} consecutive days\n'.format(x[2], x[1]))

			neg = list(filter(lambda x: x[1] == '-', tentative_list))
			pos = list(filter(lambda x: x[1] == '+', tentative_list))

			neg_num_list = [x[2] for x in neg]
			pos_num_list = [x[2] for x in pos]
			total = [x[2] for x in tentative_list]

			neg_avg = statistics.mean(neg_num_list)
			pos_avg = statistics.mean(pos_num_list)

			f.write('avg consecutive - days: {}\n'.format(neg_avg))
			f.write('avg consecutive + days: {}\n'.format(pos_avg))
			f.write('total days: {}\n'.format(sum(total)))



def run():
	consecutive()



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
# import glob

# engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

# today = datetime.now()
# today_string = today.strftime('%Y-%m-%d')

# cwd = os.getcwd()

# tentative = os.path.join(cwd, 'tickers/tentative', '{}.txt'.format(today_string))
# ticker_list = os.path.join(cwd, 'tickers', 'tickers.txt')
# bargraph = os.path.join(cwd, 'analysis/open_close/bargraph')

# price_limit = 50

# limit = 30

# tentative_list = []

# def get_data(ticker):
# 	sql = """
# 			SELECT * FROM daily 
# 			WHERE Ticker = "{}"
# 			ORDER BY time DESC
# 			LIMIT {}
# 		""".format(ticker, limit)

# 	df = pd.read_sql(sql, engine)

# 	return df

# def price_filter():

# 	files = glob.glob(os.path.join(bargraph, '*'))
# 	for f in files:
# 		os.remove(f)

# 	with open(tentative, 'w') as f, open(ticker_list, 'r') as t:

# 		f.write('Filter: Price Filter\n')

# 		# for temp in ['AAPL']:
# 		for temp in t:
# 			ticker = temp.strip()

# 			df = get_data(ticker)

# 			if len(df['open']) >= (limit/2):
# 				avg_price = statistics.mean(df['open'])
# 				if avg_price >= price_limit:
# 					f.write('{}, avg price: {}\n'.format(ticker, avg_price))
# 					f.flush()
# 					calculate(ticker, df)

# def calculate(ticker, df):

# 	# y is equal to open_close values
# 	y1 = ((df['close'] - df['open'])/df['open']) * 100
# 	y2 = df['open']
# 	# x = [ x.split()[0] for x in df['date']]
# 	x = range(0, len(y1))

# 	# avg = statistics.mean(y)

# 	# consecutive = [value < 0 for value in y]
# 	# if False not in consecutive:
# 	# 	tentative_list.append(ticker)

# 	# if avg >= 0.5:
# 	# 	tentative_list.append([ticker, avg])

# 	fig, ax1 = plt.subplots()

# 	ax2 = ax1.twinx()

# 	ax1.bar(x, y1)
# 	ax2.plot(x, y2, 'b-')

# 	ax1.set_xlabel('X data')
# 	ax1.set_ylabel('close open %', color='g')
# 	ax2.set_ylabel('open price', color='b')

# 	plt.savefig(os.path.join(bargraph, '{}.png'.format(ticker)))

# 	plt.close()

# def rank_tentative():
# 	tentative_list.sort(key = lambda x: x[1], reverse = True)

# 	with open(tentative, 'a') as f:

# 		f.write('\nFilter: Avg\n')
# 		for item in tentative_list:
# 			f.write('{}, Avg: {}\n'.format(item[0], item[1]))


# def run():
# 	price_filter()
# 	rank_tentative()

