clear
discard 
estimates clear 
set linesize 255 

write_log combined

use sp_syracuse

// Drop 5 BGs that are missing median income

drop if med_inc_1k == .

// Fold the early variable to 3 categories for the ordered probit

gen fold_e = early
replace fold_e = 1 if fold_e == 2

// Build the spatial weighting matrixes 

spmatrix create contiguity C, replace
spmatrix create idistance D, replace

//
// Standard RHS variables
//

gen med_inc_100k = med_inc_1k/100

local srhs priority_fraction mean_grade dangle_fraction shr_poc med_inc_100k

//
// Ordered Probit
//

oprobit fold priority_fraction mean_grade dangle_fraction shr_poc med_inc_100k pct_res, vce(cluster District)
estimates store v_fold
margins, dydx(*) atmeans

//
// Estimating delay on reaching 25% of plowing
//

reg d25 `srhs' pct_res, vce(cluster District)
estimates store d25a

spregress d25 `srhs' pct_res, dvarlag(C) ml
estimates store d25a_s

//
// Show the results
//

set linesize 255

estimates table v_fold d25a d25a_s, star stats(N ll bic)

write_log off
