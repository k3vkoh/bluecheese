# filter a:

# try with ranking or try with buy one of each

# check the ratio of + and - days if it is + than invest when it is 2 or 3 consecutive days
 
import pandas as pd 
from sqlalchemy.types import Text
from sqlalchemy import create_engine

import matplotlib
import matplotlib.pyplot as plt

import numpy as np
from scipy.stats import norm
import statistics

from datetime import datetime

import requests

import math

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

today = datetime.now()
today_string = today.strftime('%Y-%m-%d')

def gogo(df):

	count = 0
	open_close = df['Close'] - df['Open']
	mode = None 
	if open_close[count] > 0:
		mode = 'plus'
	elif open_close[count] < 0:
		mode = 'minus'

	while True:
		if open_close[count] < 0 and mode == 'minus':
			count += 1
		elif open_close[count] > 0 and mode == 'plus':
			count += 1
		else:
			break

	return [count, mode]


def invest(investable, ticker, openp, closep, mode, count):

	if investable > 0:

		result = {'ticker': None, 'open': None, 'close': None, 'bought': None, 'sold': None, 'gain/loss': None, 'mode': None, 'count': None}
		result['ticker'] = ticker
		result['open'] = openp
		result['close'] = closep
		qtybought = investable // openp
		bought = qtybought * openp
		sold = qtybought * closep
		gainorloss = sold - bought
		result['bought'] = bought
		result['sold'] = sold 
		result['gain/loss'] = gainorloss
		result['mode'] = mode
		result['count'] = count

		return result
