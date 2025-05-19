clear
discard 
set linesize 255
write_log sp_syracuse
write_graph setup png noemf

// inputs:
//    syracuse.shp
//    syracuse.dbf
//
// outputs:
//    sp_syracuse.dta
//    sp_syracuse_shp.dta
//
// unzip the shapefile into subdirectory raw and then 
// point the shp and dbf links at the appropriate files
//

spshape2dta syracuse, replace saving(sp_syracuse)

use sp_syracuse_shp
summarize

//  replace old variables with the latest versions in the PPM dataset

use sp_syracuse

keep _ID _CX _CY GEOID

merge 1:1 GEOID using ppm_by_bg

drop if _merge == 1
tab _merge 
drop _merge 

// build a couple of new variables

gen med_inc_1k  = round(med_inc/1e3)
// gen mean_all_1k = round(mean_tav_a/1e3)
// gen mean_res_1k = round(mean_tav_r/1e3)

// update the sp dataset 

save sp_syracuse, replace 

// draw some maps

foreach v in priority_f shr_poc shr_occ med_inc_1k ///
             pct_res grade ppm d50 District {
    grmap `v', name("`v'")
    write_graph "`v'"
}

summarize

write_log off
