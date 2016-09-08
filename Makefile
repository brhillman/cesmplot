# PURPOSE: control generation of analysis plots. Specify which cases to plot as
# dependencies to the "plots" target.
#
# AUTHOR: B. Hillman, September 2016
 
ARCHIVE = /gscratch/bhillma/spcam/archive
GRAPHICS = ./graphics
REMOTE_HOST = hillmanb@lab1.atmos.washington.edu
REMOTE_DIR = ~/public_html/diagnostics/spcam

plots: $(GRAPHICS)/FSPCAMs.sp20dev.ne30_ne30.test \
	   $(GRAPHICS)/FSPCAMs.sp20.ne30_ne30.test \
	   $(GRAPHICS)/FC5.sp20dev.ne30_ne30.test

$(GRAPHICS)/%: $(ARCHIVE)/%/atm/hist/*.nc
	./quicklooks.py $^ $@

copy:
	rsync -avuP graphics/* $(REMOTE_HOST):$(REMOTE_DIR)/
