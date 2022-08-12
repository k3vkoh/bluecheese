# invest on 4 or more consecutive negative days

import pandas as pd 
from sqlalchemy.types import Text
from sqlalchemy import create_engine

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.animation import FuncAnimation

import numpy as np
from scipy.stats import norm
import statistics

from datetime import datetime, timedelta
from pytz import timezone

import os
import requests
import glob

import analysis.open_close.filter_a as fila 

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

today = datetime.now(timezone('US/Eastern'))
today_string = today.strftime('%Y-%m-%d')

cwd = os.getcwd()

ticker_list = os.path.join(cwd, 'tickers', 'tickers.txt')
sim_log = os.path.join(cwd, 'results', 'sim.txt')
sim_image = os.path.join(cwd, 'results', 'sim.png')
sim_results = os.path.join(cwd, 'results', 'results.txt')
sim_gif = os.path.join(cwd, 'results', 'sim.gif')

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
	start_dt = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days = 1)
	money = float(line.split(',')[1].strip())

final_date = data['Date'][0].split()[0]
final_dt = datetime.strptime(final_date, '%Y-%m-%d')

print('start...', start_dt)
print('end...', final_dt)
print('money...', money)

fig = plt.figure(figsize=(7,5))
plt.style.use('seaborn-deep')

listpos = []
balance_sheet = []

def init():
	plt.clf()
	plt.title('Investing on 4 or more negative consecutive days')
	plt.xlabel('Days')
	plt.ylabel('Balance')

def animate(i):
	global listpos

	listpos.append(balance_sheet[i])

	plt.plot(range(1,len(listpos)+1), listpos, color = '#00FF00')
	plt.xlim(0, len(listpos))


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

	with open(sim_results, 'a') as f:
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

			money += totalgain
			money = ((money * 100)//1)/100
			f.write('current balance: {}\n'.format(money))
			f.flush()
			add_to_log(start_dt, money, company_string)
			start_dt = start_dt + timedelta(days = 1)

def display():
	global balance_sheet

	with open(sim_log, 'r') as f:
		for x in f:
			balance_sheet.append(float(x.split(',')[1]))
	balance_sheet.reverse()

	ani = FuncAnimation(fig, animate, frames=len(balance_sheet), interval = 100, repeat=True, init_func=init)
	
	with open(sim_gif, 'wb') as gif:
		writergif = animation.PillowWriter()
		ani.save(gif, writer=writergif)

	plt.savefig(sim_image)

	plt.close()

if __name__ == '__main__':
	main()
	display()






		

