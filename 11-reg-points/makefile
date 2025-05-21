stem=ppm

$(stem).log : $(stem).do sp_syracuse.dta sp_syracuse_shp.dta
	stata /e do $< 

clean:
	@rm -fv $(stem).{txt,log}
