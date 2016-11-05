#!/bin/bash

# TODO: add a check to make sure NCO was built with UDUNITS support?

# set defaults
year1=0000
year2=9999

# parse optional arguments
while getopts ":y:Y:" opt; do
    case "$opt" in
        y)
            year1=${OPTARG}
            ;;
        Y)
            year2=${OPTARG}
            ;;
    esac
done
shift $((OPTIND-1))

# parse positional arguments
if [ $# -ge 3 ]
then
    season=$1
    outputfile=$2
    inputfiles=${@:3}
else
    echo "usage: `basename $0` [-y year1 -Y year2] <season> <outputfile> [inputfiles...]"
    exit 1
fi

# check the date range
#if [ ${year1} == 0000 || ${year2} == 9999 ]; then
#    echo "Warning: year1 and year2 are set as defaults."
#    echo "We will loop over years from 0000 to 999 and this will take"
#    echo "a heck of a long time and probably generate a lot of error noise."
#fi

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

if test "${season_months[$season]+isset}"; then
    months=(${season_months[$season]})
else
    echo "Season $season is not defined."
    exit 1
fi

nmonths=${#months[@]}
years=(`seq 2000 2012`)
for year in ${years[@]}; do
    # find date range for this season
    if [ ${season} == 'DJF' ]; then
        year1=$((year - 1))
    else
        year1=${year}
    fi
    year2=${year}
    date1=${year1}-${months[0]}-01
    date2=${year2}-${months[${nmonths}-1]}-31

    # calculate seasonal average for this year
    seasonal_mean=tmp.${season}_${year}.nc
    ncra -O -d time,${date1},${date2} ${inputfiles} ${seasonal_mean}
    if [ $? -eq 0 ]; then
        seasonal_means=(${seasonal_means[@]} ${seasonal_mean})
    else
        rm -f ${seasonal_mean}.*.tmp
    fi
done

# calculate climatology from seasonal means
ncra -O ${seasonal_means[@]} ${outputfile}

# clean up temporary files
rm -f ${seasonal_means[@]}

# exit gracefully
exit 0
