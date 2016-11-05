#!/bin/bash

# TODO: add a check to make sure NCO was built with UDUNITS support?

# set defaults
year1=0000
year2=9999

usage="usage: `basename $0` [--year1 year] [--year2 year] [--stddev file] [-h] <season> <outputfile> <inputfiles...>"
help_msg="
    ${usage}                                                                    
                                                                                
    POSITIONAL ARGUMENTS                                                        
    season          Season to calculate climatologies for. Valid options are
                        DJF: December, January, and February (in order; script
                             will use December from previous year appropriately)
                        MAM: March, April, and May
                        JJA: June, July, and August
                        SON: September, October, and November
                        ANN: Annual climatology (all months)
                        01, ..., 12: Monthly climatology

    outputfile      Name of output file to store climatological means in
    inputfile[s]    List of input files to calculate climatologies over.
                    Input files will be searched for valid dates within range
                    specified by year1 and year2 for each season, and then
                    climatology statistics calculated over each (years) seasonal
                    means.
                                                                                
    OPTIONAL ARGUMENTS                                                          
    -y, --year1 [year]
                    First year to consider for climatology calculations. Default
                    is 0000, but note that not selecting an optional start year 
                    will cause the script to loop over all years looking for    
                    valid data, which will take a lot longer than you probably  
                    want.                                                       

    -Y, --year2 [year]
                    Last year to consider for climatology calculations. Default 
                    is 9999, but again note that not selecting an optional end  
                    year wll cause the script to loop over all years looking for
                    valid data, which is probably not what you want.            

    -s, --stddev [file]
                    File to save standard deviation statistics to. If not present
                    then standard deviation statistics will not be calculated.

    -h, --help      Display this help message and exit.                         
    
    IMPORTANT NOTES
    This script attempts to calculate seasonal climatologies from arbitrary
    NetCDF input files. This relies on the input files having \"time\" defined as
    a record dimension, and on udunits being able to interpret the time units.
    This DEPENDS on the netcdf operators being built with udunits support. This
    script MAY NOT raise any errors if the netcdf operators are build without
    udunits, but the results will be GARBAGE! Extensive testing has not been done
    to confirm how this script may fail, so use at your own risk!

    GETTING DEPENDENCIES
    An easy way of getting a working udunits/nco is to install the Anaconda
    package manager (designed for managing python packages) and then to install
    nco via conda using:

        conda install -c conda-forge nco

    This should install a working nco with udunits support (at least it did in my
    case).

    ORIGINAL AUTHOR
    Benjamin R. Hillman (bhillma@sandia.gov; benjaminr.hillman@gmail.com)
"

# parse optional arguments
while [ "$1" != "" ]; do
    case "$1" in
        -y | --year1)
            shift; year1=$1;;
        -Y | --year2)
            shift; year2=$1;;
        -s | --stddev)
            shift; stdfile=$1;;
        -h | --help)
            printf "${help_msg}"; exit 0;;
        -*)
            printf "${usage}"; exit 1;;
        *)
            break;;
    esac
    shift
done
            
# parse positional arguments
if [ $# -ge 3 ]
then
    season=$1
    outputfile=$2
    inputfiles=${@:3}
else
    echo ${usage}; exit 1
fi

# check the date range
if [ "${year1}" == "0000" ] && [ "${year2}" == "9999" ]; then
    echo "Warning: year1 and year2 are set as defaults."
    echo "We will loop over years from 0000 to 9999 and this will take"
    echo "a heck of a long time and probably generate a lot of error noise."
fi

# define the seasons
declare -A season_months
season_months[DJF]="12 01 02"
season_months[MAM]="03 04 05"
season_months[JJA]="06 07 08"
season_months[SON]="09 10 11"
season_months[ANN]="01 02 03 04 05 06 07 08 09 10 11 12"
for m in `seq -w 01 12`; do
    season_months[$m]=$m
done

# make sure "season" was set properly; if it was, then set the months variable
# to the months that make up this season; if it was not, then exit with error.
if test "${season_months[$season]+isset}"; then
    months=(${season_months[$season]})
else
    echo "Season $season is not defined."
    exit 1
fi

# Start loop over years. We look for valid time samples for the selected season
# for each year in the specified date range. A seasonal average is calculated for
# each year in which we found valid dates. The time series of seasonal averages
# is then used to calculate the climatologies. TODO: add option to calculate the
# climatological standard deviation.
echo "Calculating seasonal averages for each season from ${year1} to ${year2}..."
nmonths=${#months[@]}
years=(`seq ${year1} ${year2}`)
found_years=()
for year in ${years[@]}; do
    # find date range for this season
    if [ ${season} == 'DJF' ]; then
        y1=$((year - 1))
    else
        y1=${year}
    fi
    y2=${year}
    date1=${y1}-${months[0]}-01
    date2=${y2}-${months[${nmonths}-1]}-31

    # calculate seasonal average for this year
    seasonal_mean=tmp.${season}_${year}.nc
    ncra -O -d time,${date1},${date2} ${inputfiles} ${seasonal_mean}
    if [ $? -eq 0 ]; then
        seasonal_means=(${seasonal_means[@]} ${seasonal_mean})
        found_years=(${found_years[@]} ${year})
    else
        echo "ncra failed for ${year}."
        rm -f ${seasonal_mean}.*.tmp
    fi
done

# calculate climatology from seasonal means
echo "Calculating seasonal climatology from seasonal means from \
${found_years[0]} to ${found_years[${#found_years[@]}-1]}..."
ncra -O ${seasonal_means[@]} ${outputfile}; ncwa -O -a time ${outputfile} ${outputfile}
ncatted -O -a years_averaged,global,o,c,"${found_years[0]}-${found_years[${#found_years[@]}-1]}" ${outputfile}

# calculate standard deviation from seasonal means
if [ "${stdfile}" != "" ]; then
    echo "Calculating temporal standard deviations from seasonal means..."
    ncrcat -O ${seasonal_means[@]} ${stdfile}
    ncbo -O ${stdfile} ${outputfile} tmp.std.nc && mv -f tmp.std.nc ${stdfile}
    ncwa -O -a time -y rmssdn ${stdfile} ${stdfile}
fi

# clean up temporary files
rm -f ${seasonal_means[@]}

# exit gracefully
echo "Done."
exit 0
