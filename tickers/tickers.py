def get_tickers():

	with open('nasdaq.csv', 'r') as nd, open('nyse.csv', 'r') as ny, open('tickers.txt', 'w') as t:

		for line in nd:
			temp = line.split(',')
			if temp[0] != 'Symbol':
				t.write('{}\n'.format(temp[0]))	

		for line in ny:
			temp = line.split(',')
			if temp[0] != 'Symbol':
				t.write('{}\n'.format(temp[0]))	

def main():
	get_tickers()

if __name__ == '__main__':
	main()