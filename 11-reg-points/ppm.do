/*
PPM regressions
Mar 2024

Also runs count on city_miles and ppm regressors
*/

clear
discard 
set linesize 255
write_log ppm
write_graph setup ana png noemf

use sp_syracuse

gen med_inc_100k = med_inc_1k/100

spmatrix create contiguity C, replace
spmatrix create idistance D, replace

local phys priority_fraction mean_grade dangle_fraction
local demo med_inc_100k shr_poc

reg ppm `phys' `demo' pct_res
estimates store r2v2

spregress ppm `phys' `demo' pct_res, dvarlag(C) ml force
estimates store r2v2_C

estimates table r2v2 r2v2_C, star stats(N ll bic)
