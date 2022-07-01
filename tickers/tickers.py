def get_tickers():

	with open('t1.csv', 'r') as t1, open('t2.csv', 'r') as t2, open('tickers.txt', 'w') as t:

		for line in t1:
			temp = line.split(',')
			if temp[0] != 'Symbol':
				t.write('{}\n'.format(temp[0]))	

		for line in t2:
			temp = line.split(',')
			if temp[0] != 'Symbol':
				t.write('{}\n'.format(temp[0]))			



def main():
	get_tickers()


if __name__ == '__main__':
	main()