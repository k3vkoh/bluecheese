import collect_data.get_daily as daily
import analysis.open_close.filter_a as fila 

def main():
	daily.main()
	fila.run()

if __name__ == '__main__':
	main()