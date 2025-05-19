_check.log : _check.py snowplow_trim.gpkg
	python3 _check.py

snowplow_trim.gpkg : snowplow.py ../01-plow-data/*.csv
	python3 snowplow.py

clean:
	@rm -fv snowplow_trim.{gpkg,csv,pkl} _check.log
