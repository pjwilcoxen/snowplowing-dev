sp_syracuse.dta : sp_syracuse.do syracuse_bg.dbf syracuse_bg.shp ppm_by_bg.dta
	stata /e do sp_syracuse.do

clean:
	@rm -fv sp_syracuse.{dta,txt} sp_syracuse_shp.dta figs/*.png 
