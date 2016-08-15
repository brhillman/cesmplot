# define some cesm utilities
# these should go into a separate package
import numpy, xarray
import nclpy  # my port of NCL fortran routines to Python

def area_average(vdata, lat):
    weights = numpy.cos(numpy.pi * lat / 180.0) * vdata / vdata
    return (weights * vdata).sum() / weights.sum()


def area_rmse(vtest, vcntl, lat):
    weights = numpy.cos(numpy.pi * lat / 180.0) * vdata / vdata * vcntl / vcntl
    return numpy.sqrt((weights * (vtest - vcntl) ** 2).sum() / weights.sum())

    
def get_var_at_plev(ds, vname, plev):
    vname_plev = '%s%0f'%(vname, plev)
    if vname_plev in ds:
        print(vname + ' exists'); stdout.flush()
        return ds[vname_plev]
    else:
        # Interpolate to pressure level
        # TODO: implement this in python?
        # This also needs some smarter dimension checking
        vint = nclpy.vinth2p(
            ds[vname].transpose('time', 'ncol', 'lev'), ds.hyam, ds.hybm, 
            1e-2 * ds.P0, ds.PS, numpy.array([plev,]), 
            method=2, fill_value=-999, extrapolate=0,
        )
        vint = xarray.DataArray(
            vint,
            dims=('time', 'ncol', 'plev'), coords={'time': ds.time, 'ncol': ds.ncol, 'plev': [plev,]},
            attrs={'long_name': '%.0f hPa %s'%(plev, ds[vname].long_name.lower()), 'units': ds[vname].units}
        )
        # add to dataset
        #ds.update({vname_plev: vint})
        
        return vint
    
    
def get_var(ds, vname):
    if vname == 'U850':
        return get_var_at_plev(ds, 'U', 850)
    elif vname == 'U500':
        return get_var_at_plev(ds, 'U', 500)
    elif vname == 'U250':
        return get_var_at_plev(ds, 'U', 250)
    elif vname == 'U200':
        return get_var_at_plev(ds, 'U', 200)
    elif vname == 'U0':
        return ds['U'].isel(lev=0)
    elif vname == 'V850':
        return get_var_at_plev(ds, 'V', 850)
    elif vname == 'V500':
        return get_var_at_plev(ds, 'V', 500)
    elif vname == 'V250':
        return get_var_at_plev(ds, 'V', 250)
    elif vname == 'Z500':
        return get_var_at_plev(ds, 'Z3', 500)
    elif vname == 'T850':
        return get_var_at_plev(ds, 'T', 850)
    elif vname == 'T250':
        return get_var_at_plev(ds, 'T', 250)
    elif vname == 'NETCF':
        netcf = ds['SWCF'] + ds['LWCF']
        netcf.attrs = ds['SWCF'].attrs
        netcf.attrs.update({'long_name': 'Net cloud radiative effect'})
        return  netcf
    else:
        return ds[vname]
    

def get_datetimes(ds):
    import pandas
    dates = ds.date
    datesecs = ds.datesec
    hours = datesecs / 3600
    fulldates = ['%i%02i'%(d, h) for (d, h) in zip(dates, hours)]
    return pandas.to_datetime(fulldates, format='%Y%m%d%H')