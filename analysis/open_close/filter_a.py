# filter a:

# try with ranking or try with buy one of each
 
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
	positive = False
	open_close = df['close'] - df['open']

	while not positive:
		if open_close[count] < 0:
			count += 1
		else:
			positive = True

	if count < 3:
		return False

	return True

def invest(investable, ticker, openp, closep):

	if investable > 0:

		result = {'ticker': None, 'open': None, 'close': None, 'bought': None, 'sold': None, 'gain/loss': None}
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

		return result
