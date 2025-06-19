// counter.do
// Nov 2023 PJW
//
// Run counterfactuals on plowing regressions.
//

clear
discard 
write_graph setup png noemf 

estimates clear 

write_log counter

use sp_syracuse

// Some BGs are missing median income

drop if med_inc_1k == .

// Build the spatial weighting matrixes 

spmatrix create contiguity C, replace
spmatrix create idistance D, replace

//
// Standard RHS variables
//

gen med_inc_100k = med_inc_1k/100

local srhs priority_fraction mean_grade dangle_fraction shr_poc med_inc_100k

spregress d25 `srhs' pct_res, dvarlag(C) ml
estimates store d25a_s

// Generate fitted values

predict fit
gen res = d25 - fit
graph box res, over(District) ///
    title("Residuals by District") ///
    name("resid")

write_graph "resid"

// Generate counterfactual with mean POC share 

sum shr_poc 
gen orig_shr_poc = shr_poc
replace shr_poc = r(mean)
sum shr_poc 

predict counter
gen diff = counter-fit
summ diff

hist diff, percent ///
   title("Difference in d25 with counterfactural shr_poc") ///
   xtitle("Hours") ///
   note("Note: counterfactual - fitted") ///
   name("cdiff")
   
write_graph "cdiff"

local keepers GEOID orig_shr_poc d25 fit res shr_poc counter diff 

outsheet `keepers' using counter.csv, comma names replace 

//
// Show the results
//

set linesize 255
estimates table *, star stats(N ll aic)

write_log off
