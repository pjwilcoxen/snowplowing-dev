stem=priority

$(stem).log : $(stem).do sp_syracuse.dta sp_syracuse_shp.dta
	/c/Program\ Files/Stata16/StataIC-64.exe /e do $< 

clean:
	@rm -fv $(stem).{txt,log}
