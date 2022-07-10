import requests
import json
from datetime import datetime, timedelta
import pandas as pd 
from sqlalchemy.types import Text
from sqlalchemy import create_engine
import os
import yfinance as yf 

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

cwd = os.getcwd()

ticker_list = os.path.join(cwd, 'tickers', 'tickers.txt')
log = os.path.join(cwd, 'collect_data', 'daily_log.txt')

d = open(log, 'r')
start_string = d.readline().strip()
d.close()
today = datetime.now()
today_string = today.strftime('%Y-%m-%d')

tracker = os.path.join(cwd, 'collect_data/tracker', '{}.txt'.format(today_string))
track = open(tracker, 'w')

errors = 0

dataframe = pd.DataFrame()

def add_to_log(date):
	with open(log, 'r+') as f:
		content = f.read()
		f.seek(0)
		f.write(date + '\n' + content)
		f.flush()

def download(tickers, ticlist):
	global dataframe, errors

	try:
		data = yf.download(tickers, start = start_string, end = today_string, group_by = 'ticker')
		for ticker in ticlist:
			temp = data.copy(deep = True)
			temp = temp[ticker]
			temp['Ticker'] = ticker
			dataframe = pd.concat([dataframe, temp])
		return "{} done\n".format(tickers)
	except:
		errors += 1
		return "{} error\n".format(tickers)


def collect():

	print('TimeFrame')
	print(start_string)
	print(today_string)
	print("STARTING ...")

	with open(ticker_list, 'r') as file:

		count = 0
		tickers = ''
		ticlist = []
		while True:
			line = file.readline()

			if not line:
				tickers = tickers.strip()
				message = download(tickers, ticlist)
				track.write(message)
				track.flush()
				break

			count += 1
			ticker = line.strip()
			tickers = tickers + ' ' + ticker 
			ticlist.append(ticker)

			if count == 100:
				tickers = tickers.strip()
				message = download(tickers, ticlist)
				track.write(message)
				track.flush()
				count = 0 
				tickers = ''
				ticlist = []

	df = pd.DataFrame(data = dataframe)
	df.to_sql('daily', engine, if_exists = 'append', index = False)

	add_to_log(today_string)
	print("DONE")

def main():
	collect()
	track.close()
	