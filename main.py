import collect_data.get_daily as daily
import analysis.open_close.filter_a as fila 

def main():

	mode = int(input("1: collect, 2: filter a, 3: both "))
	if mode == 1:
		daily.main()
	elif mode == 2:
		fila.run()
	elif mode == 3:
		daily.main()
		fila.run()

if __name__ == '__main__':
	main()