# filter a:
# compiles a list of tickers that meet the following criteria:
# first find the outlier number of days that are consecutive plus and minus 
# then calculate avg number of days consecutive plus and minus 
# invest in only ones that can only be not rounded 
# find the ratio of days that match the avg 

# get data is now in main and simulation


# when you look to invest make sure you look at one more day than the average
 
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

def consecutive(ticker, df):

	tentative_list = []

	open_close = df['close'] - df['open']

	avg_change = statistics.mean(open_close)

	i = df.shape[0] - 1 
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
					tentative_list.append([ticker, '+', consecutive_pos, avg_change])
				else:
					tentative_list.append([ticker, '-', consecutive_neg, avg_change])
			else:
				i -= 1
				if i == 0:
					if consecutive_pos:
						consecutive_pos += 1
						tentative_list.append([ticker, '+', consecutive_pos, avg_change])
					else:
						consecutive_neg += 1
						tentative_list.append([ticker, '-', consecutive_neg, avg_change])
		i -= 1

	return tentative_list

def find_outliers(tentative_list):

	dataset = sorted([x[2] for x in tentative_list])
	q1, q3 = np.percentile(dataset,[25,75])
	iqr = q3 - q1
	lower_bound = q1 - (1.5 * iqr)
	upper_bound = q3 + (1.5 * iqr)
	valid = list(filter(lambda x: x[2] <= upper_bound and x[2] >= lower_bound, tentative_list))
	return valid

def indicator(filtered_list):

	neg = list(filter(lambda x: x[1] == '-', filtered_list))
	pos = list(filter(lambda x: x[1] == '+', filtered_list))

	neg_num_list = [x[2] for x in neg]
	pos_num_list = [x[2] for x in pos]
	total = [x[2] for x in filtered_list]

	neg_avg = statistics.mean(neg_num_list)
	pos_avg = statistics.mean(pos_num_list)

	magic_number = math.ceil(neg_avg)

	return magic_number

def gogo(df, magic_number):

	open_close = df['close'] - df['open']

	negative_days = open_close[: magic_number]
	positive_day = open_close[magic_number]

	for day in negative_days:
		if day > 0:
			return False

	if positive_day < 0:
		return False

	return True





