_check.log : _check.py ppm_by_bg.dta
	python3 _check.py

ppm_by_bg.dta : ppm_by_bg.py ppm-by-hour.pkl
	python3 ppm_by_bg.py

ppm-by-hour.pkl : ppm-by-hour.py bg-merge.pkl points-by-bg-hour.pkl
	python3 ppm-by-hour.py

clean :
	rm -rvf *.{log,csv,png,bak,dta} *~ {_check,ppm-by-hour}.pkl
