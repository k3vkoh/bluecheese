import pandas as pd 
from sqlalchemy.types import Text
from sqlalchemy import create_engine

import matplotlib
import matplotlib.pyplot as plt

import numpy as np
import statistics

from datetime import datetime

import os

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

today = datetime.now()
today_string = today.strftime('%Y-%m-%d')

cwd = os.getcwd()

month = '06'
year = '2022'

date_string = year + "-" + month

sql = """
		SELECT * FROM daily 
		WHERE Ticker = 'AAPL'
	"""
df = pd.read_sql(sql, engine)
df2 = df.loc[df['Date'].str.contains(date_string)]
rowcount = df2.shape[0]

ticker_path = os.path.join(cwd, 'tickers', 'tickers.txt')
rank_path = os.path.join(cwd, 'rank', '{}.txt'.format(date_string))

def get_data():
	sql = """
			SELECT * FROM daily 
		"""

	df = pd.read_sql(sql, engine)

	temp = df.loc[df['Date'].str.contains(date_string)]

	return temp


def rank():

	rank_list = []

	try:
		df = get_data()
	except:
		print('error')
		return

	with open(ticker_path, 'r') as t:

		# for temp in ['AERC']:
		for temp in t:
			ticker = temp.strip()
			temp = df.loc[df['Ticker'] == ticker]
			open_close = temp['Close'] - temp['Open']
			nonna_values = open_close.notna()
			open_close = open_close[nonna_values]
			if open_close.size == rowcount:
				sum_oc = sum(open_close)
				rank_list.append([ticker, sum_oc])

	rank_list.sort(key = lambda x: x[1], reverse = True)

	with open(rank_path, 'w') as f:
		f.write('Ranking for {}-{}\n\n'.format(month, year))
		f.write('All Tickers:\n')
		for x in rank_list:
			f.write('Ticker: {} Average: {}\n'.format(x[0], x[1]))
		f.write('Top 5:\n')
		count = 1
		for x in rank_list[:5]:
			f.write('{}. Ticker: {} Average: {}\n'.format(count, x[0], x[1]))	
			count += 1

if __name__ == '__main__':
	rank()



		

