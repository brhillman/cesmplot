#!/usr/bin/env python3
import xarray
from cesmutils import get_datetime

def main(season, outputfile, *inputfiles):
    season_months = {'JJA': [6, 7, 8],
                     'SON': [9, 10, 11],
                     'DJF': [12, 1, 2],
                     'MAM': [3, 4, 5],
                     'ANN': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
    
    with xarray.open_mfdataset(*inputfiles, decode_times=False) as ds:
        ds.coords['time'] = get_datetime(ds)
        ds_months = ds.grouby('time.month').mean('time', keep_attrs=True)
        ds_climo = ds_months.sel_points(month=season_months[season]).mean('points', keep_attrs=True)
        ds_climo.to_netcdf(outputfile)


if __name__ == '__main__':
    import plac; plac.call(main)
