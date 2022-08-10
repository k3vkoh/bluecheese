import pandas as pd 
from sqlalchemy.types import Text
from sqlalchemy import create_engine

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.animation import FuncAnimation

import seaborn as sns

import numpy as np
import statistics

from datetime import datetime
from pytz import timezone

import os

engine = create_engine('sqlite:////Users/kevinkoh/Desktop/bluecheese/bluecheese.db')

year = 2022
month = 7
date_string = None 
if month < 10:
	date_string = '{}-0{}'.format(year, month)
else:
	date_string = '{}-{}'.format(year, month)

cwd = os.getcwd()

ticker_path = os.path.join(cwd, 'tickers', 'tickers.txt')
rank_path = os.path.join(cwd, 'rank', '{}.txt'.format(date_string))
gif_path = os.path.join(cwd, 'rank', '{}.gif'.format(date_string))
png_path = os.path.join(cwd, 'rank', '{}.png'.format(date_string))
movement_path = os.path.join(cwd, 'rank', '{}_movement.gif'.format(date_string))
finalmove_path = os.path.join(cwd, 'rank', '{}_movement.png'.format(date_string))

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

animatelabel = []
animatedata = []

palette = list(reversed(sns.color_palette("Spectral", 10).as_hex()))

fig = plt.figure(figsize=(7,5))
plt.style.use('seaborn-deep')

listpos = {}

def get_data():

	sql = """
			SELECT * FROM prod 
			WHERE Date BETWEEN '{}' AND '{}'
			ORDER BY Date DESC
		""".format(start, end)

	df = pd.read_sql(sql, engine)
 
	return df

def init():
	plt.clf()
	plt.xlabel('% Change')
	plt.title('Best Stocks for {}'.format(date_string))

def init2():
	plt.clf()

def animate(i):

	y0 = sum(animatedata[0][:i+1])
	y1 = sum(animatedata[1][:i+1])
	y2 = sum(animatedata[2][:i+1])
	y3 = sum(animatedata[3][:i+1])
	y4 = sum(animatedata[4][:i+1])
	y5 = sum(animatedata[5][:i+1])
	y6 = sum(animatedata[6][:i+1])
	y7 = sum(animatedata[7][:i+1])
	y8 = sum(animatedata[8][:i+1])
	y9 = sum(animatedata[9][:i+1])

	minval = min([y0,y1,y2,y3,y4,y5,y6,y7,y8,y9])
	maxval =  max([y0,y1,y2,y3,y4,y5,y6,y7,y8,y9])
	minx = 0
	maxx = 500
	if minval < 0:
		minx = minval
	if maxval > 500:
		maxx = maxval
	plt.xlim(minx, maxx)

	plt.barh(range(10), sorted([y0,y1,y2,y3,y4,y5,y6,y7,y8,y9]), color=palette)

	tickdic = {}
	for x in range(10):
		tickdic[animatelabel[x]] = sum(animatedata[x][:i+1])

	sorted_tickdic = sorted(tickdic.items(), key=lambda x: x[1])

	tcks = [i[0] for i in sorted_tickdic]

	plt.yticks(np.arange(10), tcks)


def animate2(i):

	plt.clf()

	plt.xlabel('Days Elapsed')
	plt.title('Rank of Best Stocks for {}'.format(date_string))

	tickdic = {}
	for x in range(10):
		tickdic[animatelabel[x]] = sum(animatedata[x][:i+1])

	sorted_tickdic = sorted(tickdic.items(), key=lambda x: x[1])

	tcks = [i[0] for i in sorted_tickdic]

	j = 0
	while j < len(animatelabel):
		if animatelabel[j] not in listpos:
			listpos[animatelabel[j]] = [tcks.index(animatelabel[j])]
		else:
			listpos[animatelabel[j]].append(tcks.index(animatelabel[j]))
		plt.plot(np.arange(len(listpos[animatelabel[j]])), listpos[animatelabel[j]], color = palette[j])
		plt.annotate(animatelabel[j], (len(listpos[animatelabel[j]])-1, listpos[animatelabel[j]][-1] ))
		j += 1

	plt.yticks(np.arange(10), np.arange(1,11)[::-1])

	plt.xlim(0, rowcount)

def rank():

	global animatelabel, animatedata

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

	with open(rank_path, 'r+') as f:
		content = f.read()
		f.seek(0)
		f.write('Top 10:\n')
		rank_list.sort(key = lambda x: x[1], reverse = True)
		count = 1
		for x in rank_list[:10]:
			f.write('{}. Ticker: {} Average: {}\n'.format(count, x[0], x[1]))	
			count += 1
		f.write('\n' + content)
		f.flush()

	for x in rank_list[:10]:
		temp = open_close.loc[df['Ticker'] == x[0]]
		temp.reset_index(drop=True, inplace=True)
		temp = temp.values
		animatelabel.append(x[0])
		animatedata.append(temp)

	ani = FuncAnimation(fig, animate, frames=rowcount, interval = 1000, repeat=True, init_func=init)
	
	with open(gif_path, 'wb') as gif:
		writergif = animation.PillowWriter()
		ani.save(gif, writer=writergif)

	plt.savefig(png_path)

	ani = FuncAnimation(fig, animate2, frames=rowcount, interval = 1000, repeat=True, init_func=init2)
	
	with open(movement_path, 'wb') as move:
		writergif = animation.PillowWriter()
		ani.save(move, writer=writergif)

	plt.savefig(finalmove_path)

if __name__ == '__main__':
	rank()
