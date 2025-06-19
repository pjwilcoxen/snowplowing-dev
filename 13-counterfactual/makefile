stem=counter

.precious: $(stem).log 

figs/f5-diff.png : $(stem).log plot.py
	python3 plot.py

$(stem).log : $(stem).do sp_syracuse.dta sp_syracuse_shp.dta
	stata /e do $< 

clean:
	@rm -fv $(stem).{txt,log} figs/*.png
