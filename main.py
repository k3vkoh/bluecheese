import collect_data.get_daily as daily
import simulation as sim

from datetime import datetime
from pytz import timezone
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

	sim.main()

if __name__ == '__main__':
	main()