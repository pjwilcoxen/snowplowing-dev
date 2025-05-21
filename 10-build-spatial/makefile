sp_syracuse.dta : sp_syracuse.do syracuse.dbf syracuse.shp ppm_by_bg.dta
	stata /e do sp_syracuse.do

clean:
	@rm -fv sp_syracuse.{dta,txt} sp_syracuse_shp.dta figs/*.png 
