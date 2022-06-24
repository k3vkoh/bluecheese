order of file execution:

1. collect_data/get_daily
- this will write to:
	- daily_log
	- tickers/tracker
	- the database

2. analysis/open_close/filter_a
- this will write to:
	- tickers/tentative
- this will draw bargraphs to bargraph

- then it will append to the tentative with the second list