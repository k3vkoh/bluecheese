# invest on 4 or more consecutive negative days

# dynamic porfolio needs to be added

import pandas as pd 
from sqlalchemy.types import Text
from sqlalchemy import create_engine

import matplotlib
import matplotlib.pyplot as plt

import numpy as np
from scipy.stats import norm
import statistics

from datetime import datetime, timedelta
from pytz import timezone

import os
import requests
import glob
import math 

import analysis.open_close.filter_a as fila 

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

today = datetime.now(timezone('US/Eastern'))
today_string = today.strftime('%Y-%m-%d')

cwd = os.getcwd()

ticker_list = os.path.join(cwd, 'tickers', 'tickers.txt')
sim_log = os.path.join(cwd, 'results', 'sim.txt')
sim_image = os.path.join(cwd, 'results', 'sim.png')

sql = """
		SELECT * FROM prod 
		WHERE Ticker = 'AAPL'
		ORDER BY Date DESC
		LIMIT 1
	"""

data = pd.read_sql(sql, engine)

with open(sim_log, 'r') as s:

	line = s.readline()
	start_date = line.split(',')[0]
	start_dt = datetime.strptime(start_date, '%Y-%m-%d')
	money = float(line.split(',')[1].strip())

final_date = data['Date'][0].split()[0]
final_dt = datetime.strptime(final_date, '%Y-%m-%d')

print('start...', start_dt)
print('end...', final_dt)
print('money...', money)

def add_to_log(date, money, companies):

	date_string = date.strftime('%Y-%m-%d')

	with open(sim_log, 'r+') as f:
		content = f.read()
		f.seek(0)
		f.write('{}, {}, {}\n{}'.format(date_string, money, companies, content))
		f.flush()

def get_data(ticker):

	end = start_dt
	start = end + timedelta(days = -30)

	sql = """
			SELECT * FROM prod 
			WHERE Ticker = '{}' and Date BETWEEN '{}' AND '{}'
			ORDER BY Date DESC
		""".format(ticker, start, end)

	df = pd.read_sql(sql, engine)

	return df


def thumbsup():

	final = []

	for temp in ['AAPL', 'AMZN', 'TSLA', 'MSFT', 'GOOGL']:

		ticker = temp.strip()

		try:
			df = get_data(ticker)
		except:
			print('error')
			continue

		result = fila.gogo(df)
		count = result[0]
		mode = result[1]

		if mode == 'minus' and count >= 4:
			final.append([ticker, mode, count])

	return final

def main():

	global money, start_dt

	sim_results = os.path.join(cwd, 'results/sim', '{}.txt'.format(start_dt))

	with open(sim_results, 'w') as f:
		while start_dt <= final_dt:
			print('{}'.format(start_dt))
			f.write('\n{}\n'.format(start_dt))
			f.flush()
			final = thumbsup()
			totalgain = 0
			company_string = ''
			for value in final:
				start = start_dt
				end = start_dt + timedelta(days = 1)
				ticker = value[0]
				mode = value[1]
				count = value[2]
				sql = """
						SELECT * FROM prod 
						WHERE Ticker = '{}' and Date BETWEEN '{}' AND '{}'
						ORDER BY Date DESC
					""".format(ticker, start, end)
				df = pd.read_sql(sql, engine)
				if df.shape[0] != 1:
					continue
				company_string += '{} '.format(ticker)
				result = fila.invest(money * (1/len(final)), ticker, df['Open'][0],  df['Close'][0], mode, count)
				totalgain += result['gain/loss']
				f.write('{}, Open: {}, Close: {}, Bought: {}, Sold: {}, Gain/Loss: {}, Mode: {}, Count: {}\n'.format(result['ticker'], result['open'], result['close'], result['bought'], result['sold'], result['gain/loss'], result['mode'], result['count']))
				f.flush()

			money += math.floor(totalgain * 100)/ 100
			f.write('current balance: {}\n'.format(money))
			f.flush()
			add_to_log(start_dt, money, company_string)
			start_dt = start_dt + timedelta(days = 1)

	display()

def display():
	balance_sheet = []
	with open(sim_log, 'r') as f:
		for x in f:
			balance_sheet.append(int(x.split(',')[1]))
	plt.plot(range(0, len(balance_sheet)), balance_sheet)
	plt.title('Investing on 4 or more negative consecutive days')
	plt.xlabel('Days')
	plt.ylabel('Balance')
	plt.savefig(sim_image)
	plt.close()

if __name__ == '__main__':
	main()






		

