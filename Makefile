################################################################################
# 
# PURPOSE: control generation of analysis plots.
#
# AUTHOR: B. Hillman, September 2016
#
################################################################################
 
# Locations for model output, data, figures, etc.
# Will probably need to build in some additional logic at some point to handle
# output from different models, which may be stored under different directories.
ARCHIVE = /gscratch/bhillma/spcam/archive
GRAPHICS = ./graphics
OBS_ROOT = /gscratch/bhillma/obs
REMOTE_HOST = hillmanb@lab1.atmos.washington.edu
REMOTE_DIR = ~/public_html/diagnostics/spcam

# Cases to compare and identifier for this comparison
#CASES := FSPCAMs.sp20.ne30_ne30.test FSPCAMm.sp20.ne30_ne30.test
#NAME := test.test2
#ifeq ($(NAME),test.test2)
#	CASES := FC5.sp20.ne30_ne30.test FC5.sp20.ne30_ne30.test2
#endif
#ifeq ($(NAME),test.mycosp)
#	CASES := FC5.sp20.ne30_ne30.test FC5.sp20.ne30_ne30.mycosp
#endif

TEST_CASE := FC5.sp20b.ne30_ne30.mycosp
CNTL_CASE := FC5.sp20b.ne30_ne30.test

NAME := $(TEST_CASE).vs.$(CNTL_CASE)
CASES := $(TEST_CASE) $(CNTL_CASE)
DATE := 0001-01-01-03600

# Lists of variables to plot
map_vars := \
		cltmisr cllmisr clmmisr clhmisr \
		cltisccp cllisccp clmisccp clhisccp \
		cltmodis cllmodis clmmodis clhmodis \
		clwmodis climodis iwpmodis lwpmodis pctmodis \
		tautlogmodis tauwlogmodis tauilogmodis \
		tautmodis tauwmodis tauimodis reffclwmodis reffclimodis \
		CLDTOT_CS CLDTOT_CS2 \
		CLDTOT_CAL CLDLOW_CAL CLDMED_CAL CLDHGH_CAL \
		CLDLOW CLDMED CLDHGH CLDTOT \
		CLDTOT_CAL_LIQ CLDLOW_CAL_LIQ CLDMED_CAL_LIQ CLDHGH_CAL_LIQ \
		CLDTOT_CAL_ICE CLDLOW_CAL_ICE CLDMED_CAL_ICE CLDHGH_CAL_ICE \
		CLDTOT_CAL_UN CLDLOW_CAL_UN CLDMED_CAL_UN CLDHGH_CAL_UN \
		TGCLDCWP TGCLDIWP TGCLDLWP
jhist_vars := clmisr clisccp clmodis cfadDbze94

# Build lists of plots to make
map_plots := $(foreach var, $(map_vars), $(GRAPHICS)/$(NAME)/$(var).maps.pdf)
jhist_plots := $(foreach var, $(jhist_vars), $(GRAPHICS)/$(NAME)/$(var).jhist.pdf)
plots: $(map_plots) $(jhist_plots)

calipso_vars := cltcalipso cllcalipso clmcalipso clhcalipso \
	cltcalipsoliq cllcalipsoliq clmcalipsoliq clhcalipsoliq \
	cltcalipsoice cllcalipsoice clmcalipsoice clhcalipsoice \
	cltcalipsoun cllcalipsoun clmcalipsoun clhcalipsoun 

calipso_climos := \
	$(foreach var, $(calipso_vars), $(OBS_CLIMO)/$(var).climo01.nc) \
	$(foreach var, $(calipso_vars), $(OBS_CLIMO)/$(var).climo02.nc) \
	$(foreach var, $(calipso_vars), $(OBS_CLIMO)/$(var).climo03.nc) \
	$(foreach var, $(calipso_vars), $(OBS_CLIMO)/$(var).climo04.nc) \
	$(foreach var, $(calipso_vars), $(OBS_CLIMO)/$(var).climo05.nc) \
	$(foreach var, $(calipso_vars), $(OBS_CLIMO)/$(var).climo06.nc) \
	$(foreach var, $(calipso_vars), $(OBS_CLIMO)/$(var).climo07.nc) \
	$(foreach var, $(calipso_vars), $(OBS_CLIMO)/$(var).climo08.nc) \
	$(foreach var, $(calipso_vars), $(OBS_CLIMO)/$(var).climo09.nc) 

# Rules to make OBS climo files look like we need them to
# TODO: write make_climo script to accept 
# 	1) a season to average over; 
# 	2) an output file name, and 
# 	3) a list of input files to search for appropriate months
months := 01 02 03 04 05 06 07 08 09 10 11 12 
seasons := DJF JJA SON MAM ANN

$(OBS_ROOT)/clmisr.misr-ipsl.%_climo.nc: $(MISR_ROOT)/clMISR_*.nc
	@mkdir -p $(dir $@)
	./make_climo $* $@ $^

# Rules to make different kinds of plots
# TODO: we need some intermediate rules to combine files for each case or make
# climatologies first when output for each case spans multiple files.
# In particular this would be nice for zonal means so we can plot error bars for
# sampling uncertainty or variability, and possibly things like hatching on map
# plots for significance.
$(GRAPHICS)/$(NAME)/%.maps.pdf: \
		$(foreach CASE, $(CASES), $(ARCHIVE)/$(CASE)/atm/hist/*.$(DATE).nc)
	@mkdir -p $(dir $@)
	./plot_maps.py -tind 0 $* $@ $^

$(GRAPHICS)/$(NAME)/%.zonal.pdf: \
		$(foreach CASE, $(CASES), $(ARCHIVE)/$(CASE)/atm/hist/*.$(DATE).nc)
	@mkdir -p $(dir $@)
	./plot_zonal.py $* $@ $^

$(GRAPHICS)/$(NAME)/%.jhist.pdf: \
		$(foreach CASE, $(CASES), $(ARCHIVE)/$(CASE)/atm/hist/*.$(DATE).nc)
	@mkdir -p $(dir $@)
	./plot_jhists.py $* $@ $^

# Copy figures to remote directory
copy:
	rsync -avuP $(GRAPHICS)/$(NAME) $(REMOTE_HOST):$(REMOTE_DIR)/

# Remove figures (and eventually temporary files?)
clean:
	rm -f $(GRAPHICS)/$(NAME)/*.pdf
