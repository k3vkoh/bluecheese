import pandas as pd 
from sqlalchemy.types import Text
from sqlalchemy import create_engine

import matplotlib
import matplotlib.pyplot as plt

import numpy as np
import statistics

from datetime import datetime
from pytz import timezone

import os

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

today = datetime.now(timezone('US/Eastern'))
date_string = today.strftime('%Y-%m')
month = int(today.strftime('%m'))

cwd = os.getcwd()

ticker_path = os.path.join(cwd, 'tickers', 'tickers.txt')
rank_path = os.path.join(cwd, 'rank', '{}.txt'.format(date_string))

daysinmonth = [31,28,31,30,31,30,31,31,30,31,30,31]

start = date_string + '-01'
end = date_string + '-{}'.format(daysinmonth[month-1])

sql = """
			SELECT * FROM prod 
			WHERE Ticker = 'AAPL' and Date BETWEEN '{}' AND '{}'
			ORDER BY Date DESC
		""".format(start, end)

tempdf = pd.read_sql(sql, engine)

rowcount = tempdf.shape[0]

def get_data():

	sql = """
			SELECT * FROM prod 
			WHERE Date BETWEEN '{}' AND '{}'
			ORDER BY Date DESC
		""".format(start, end)

	df = pd.read_sql(sql, engine)
 
	return df


def rank():

	rank_list = []

	try:
		df = get_data()
	except:
		print('error')
		return

	open_close = ((df['Close'] - df['Open']) / df['Open']) * 100

	with open(ticker_path, 'r') as t:

		for temp in t:
			ticker = temp.strip()
			temp = open_close.loc[df['Ticker'] == ticker]
			nonna_values = temp.notna()
			temp = temp[nonna_values]
			if temp.size == rowcount:
				sum_oc = sum(temp)
				rank_list.append([ticker, sum_oc])

	with open(rank_path, 'w') as f:
		f.write('Ranking for {}\n\n'.format(date_string))
		f.write('All Tickers:\n')
		for x in rank_list:
			f.write('Ticker: {} Average: {}\n'.format(x[0], x[1]))
		f.write('Top 5:\n')
		rank_list.sort(key = lambda x: x[1], reverse = True)
		count = 1
		for x in rank_list[:5]:
			f.write('{}. Ticker: {} Average: {}\n'.format(count, x[0], x[1]))	
			count += 1

if __name__ == '__main__':
	rank()



		

