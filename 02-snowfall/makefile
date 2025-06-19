plot-snow.png : plot-snow.py noaa-data-us-units.csv hourly-2017-03.csv
	python3 plot-snow.py

hourly-2017-03.csv : hourly.py hourly-2017-03.xlsx
	python3 hourly.py

clean:
	@rm -f hourly-2017-03.csv *.png *.log
