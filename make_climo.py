#!/usr/bin/env python3
import xarray, numpy
from cesmutils import get_datetimes
from sys import stdout
from pandas import DateOffset

months = {'JJA': [6, 7, 8],
          'SON': [9, 10, 11],
          'DJF': [12, 1, 2],
          'MAM': [3, 4, 5],
          'ANN': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}

def make_climo(ds, season):

    # find unique years in concatenated inputfiles
    years = numpy.unique(ds['time.year'].values)
    print(years); stdout.flush()

    # loop over years; calculate seasonal average for each year
    seasons_list = []
    for year in years:
        # get year range for this season
        if season == 'DJF':
            year1, year2 = year - 1, year
        else:
            year1, year2 = year, year

        # date range for this season
        date1 = '%04.0f-%02.0f-01'%(year1, months[season][0])
        date2 = '%04.0f-%02.0f-31'%(year2, months[season][-1])

        # TODO: make sure dates are within range?
        if year1 < years.min() or year2 > years.max():
            continue

        # calculate mean for this season
        print('Calculate mean from %s to %s...'%(date1, date2)); stdout.flush()
        ds_season = ds.sel(time=slice(date1, date2))
        if ds_season.time.size >= len(months[season]):
            print('Found %i valid time samples...'%(ds_season.time.size)); stdout.flush()
            print(ds_season.time); stdout.flush()
            ds_season = ds_season.mean('time', keep_attrs=True)
            seasons_list.append(ds_season)

    # concatenate seasonal means into a single dataset
    print('Concatenate seasonal means...'); stdout.flush()
    ds_seasons = xarray.concat(seasons_list, dim='time', data_vars='different')

    # calculate mean climatology
    print('Calculate average of seasonal means...'); stdout.flush()
    ds_climo = ds_seasons.mean('time', keep_attrs=True)

    # calculate temporal standard deviation of seasonal means
    print('Calculate standard deviation of seasonal means...'); stdout.flush()
    ds_stdev = ds_seasons.std('time', keep_attrs=True)

    #return ds_climo, ds_stdev
    return ds_climo, ds_stdev


def main(season, outputfile, *inputfiles):

    print('Open dataset...'); stdout.flush()
    ds_in = xarray.open_mfdataset(inputfiles, decode_times=False, chunks={'time': 1})

    print('Manually decode times...'); stdout.flush()
    ds_in.coords['time'] = get_datetimes(ds_in)

    print('Calculate climotology...'); stdout.flush()
    ds_climo, ds_stdev = make_climo(ds_in, season)

    print('Write to file...'); stdout.flush()
    ds_climo.to_netcdf(outputfile)
    

if __name__ == '__main__':
    import plac; plac.call(main)
