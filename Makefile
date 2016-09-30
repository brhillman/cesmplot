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
CASES := FSPCAMs.sp20.ne30_ne30.test FSPCAMm.sp20.ne30_ne30.test
NAME := test

# Lists of variables to plot
map_vars := cltmisr cllmisr clmmisr clhmisr \
           cltisccp cllisccp clmisccp clhisccp \
           cltmodis cllmodis clmmodis clhmodis \
           clwmodis climodis iwpmodis lwpmodis pctmodis \
           tautlogmodis tauwlogmodis tauilogmodis \
           tautmodis tauwmodis tauimodis reffclwmodis reffclimodis \
           CLDTOT_CS CLDTOT_CS2 \
           CLDTOT_CAL CLDLOW_CAL CLDMED_CAL CLDHGH_CAL 
jhist_vars := clmisr clisccp clmodis cfadDbze94

# Build lists of plots to make
map_plots := $(foreach var, $(map_vars), $(GRAPHICS)/$(NAME)/$(var).maps.pdf)
jhist_plots := $(foreach var, $(jhist_vars), $(GRAPHICS)/$(NAME)/$(var).jhist.pdf)
plots: $(map_plots) $(jhist_plots)

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
$(GRAPHICS)/$(NAME)/%.maps.pdf: \
		$(foreach CASE, $(CASES), $(ARCHIVE)/$(CASE)/atm/hist/*.nc)
	@mkdir -p $(dir $@)
	./plot_maps.py $* $@ $^

$(GRAPHICS)/$(NAME)/%.zonal.pdf: \
		$(foreach CASE, $(CASES), $(ARCHIVE)/$(CASE)/atm/hist/*.nc)
	@mkdir -p $(dir $@)
	./plot_zonal.py $* $@ $^

$(GRAPHICS)/$(NAME)/%.jhist.pdf: \
		$(foreach CASE, $(CASES), $(ARCHIVE)/$(CASE)/atm/hist/*.nc)
	@mkdir -p $(dir $@)
	./plot_jhists.py $* $@ $^

# Copy figures to remote directory
copy:
	rsync -avuP $(GRAPHICS)/$(NAME) $(REMOTE_HOST):$(REMOTE_DIR)/

# Remove figures (and eventually temporary files?)
clean:
	rm -f $(GRAPHICS)/$(NAME)/*.pdf