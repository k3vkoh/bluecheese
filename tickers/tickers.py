def get_tickers():
	f = open('ticker.csv', 'r')
	t_list = open('tickers.txt', 'w')

	for line in f:
		temp = line.split(',')
		if temp[0] != 'Symbol':
			t_list.write('{}\n'.format(temp[0]))			

	f.close()
	t_list.close()


def main():
	get_tickers()


if __name__ == '__main__':
	main()