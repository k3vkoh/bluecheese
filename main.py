import collect_data.get_daily as daily

from datetime import datetime
import os

today = datetime.now(timezone('US/Eastern'))
today_string = today.strftime('%Y-%m-%d')

cwd = os.getcwd()

date_log = os.path.join(cwd, 'collect_data', 'daily_log.txt')


def main():

	f = open(date_log, 'r')
	date = f.readline().strip()
	f.close()

	if date != today_string:
		daily.main()

if __name__ == '__main__':
	main()