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
    if vname in ds.variables.keys():
        dout = ds[vname]
    elif vname == 'U850':
        dout = get_var_at_plev(ds, 'U', 850)
    elif vname == 'U500':
        dout = get_var_at_plev(ds, 'U', 500)
    elif vname == 'U250':
        dout = get_var_at_plev(ds, 'U', 250)
    elif vname == 'U200':
        dout = get_var_at_plev(ds, 'U', 200)
    elif vname == 'U0':
        dout = ds['U'].isel(lev=0)
    elif vname == 'V850':
        dout = get_var_at_plev(ds, 'V', 850)
    elif vname == 'V500':
        dout = get_var_at_plev(ds, 'V', 500)
    elif vname == 'V250':
        dout = get_var_at_plev(ds, 'V', 250)
    elif vname == 'Z500':
        dout = get_var_at_plev(ds, 'Z3', 500)
    elif vname == 'T850':
        dout = get_var_at_plev(ds, 'T', 850)
    elif vname == 'T250':
        dout = get_var_at_plev(ds, 'T', 250)
    elif vname == 'NETCF':
        netcf = ds['SWCF'] + ds['LWCF']
        netcf.attrs = ds['SWCF'].attrs
        netcf.attrs.update({'long_name': 'Net cloud radiative effect'})
        dout = netcf
    elif vname.lower() == 'clmisr':
        dout = ds['CLD_MISR']
    elif vname.lower() == 'cltmisr':
        jhist = ds['CLD_MISR']
        jhist = jhist.where(jhist.cosp_tau > 0.3)
        d = jhist.sum(dim=('cosp_tau', 'cosp_htmisr'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('cosp_tau', 'cosp_htmisr')) > 0)
        dout.attrs['long_name'] = 'Total cloud area'
        dout.attrs['units'] = ds.CLD_MISR.units
    elif vname.lower() == 'cllmisr':
        jhist = ds['CLD_MISR']
        jhist = jhist.where((jhist.cosp_tau > 0.3) & (jhist.cosp_htmisr > 0) & (jhist.cosp_htmisr < 3))
        d = jhist.sum(dim=('cosp_tau', 'cosp_htmisr'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('cosp_tau', 'cosp_htmisr')) > 0)
        dout.attrs['long_name'] = 'Low-topped cloud area'
        dout.attrs['units'] = ds.CLD_MISR.units
    elif vname.lower() == 'clmmisr':
        jhist = ds['CLD_MISR']
        jhist = jhist.where((jhist.cosp_tau > 0.3) & (jhist.cosp_htmisr > 3) & (jhist.cosp_htmisr < 7))
        d = jhist.sum(dim=('cosp_tau', 'cosp_htmisr'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('cosp_tau', 'cosp_htmisr')) > 0)
        dout.attrs['long_name'] = 'Mid-topped cloud area'
        dout.attrs['units'] = ds.CLD_MISR.units
    elif vname.lower() == 'clhmisr':
        jhist = ds['CLD_MISR']
        jhist = jhist.where((jhist.cosp_tau > 0.3) & (jhist.cosp_htmisr > 7))
        d = jhist.sum(dim=('cosp_tau', 'cosp_htmisr'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('cosp_tau', 'cosp_htmisr')) > 0)
        dout.attrs['long_name'] = 'High-topped cloud area'
        dout.attrs['units'] = ds.CLD_MISR.units
    elif vname.lower() == 'clisccp':
        dout = ds['FISCCP1_COSP']
    elif vname.lower() == 'cltisccp':
        jhist = ds['FISCCP1_COSP']
        jhist = jhist.where(jhist.cosp_tau > 0.3)
        d = jhist.sum(dim=('cosp_tau', 'cosp_prs'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('cosp_tau', 'cosp_prs')) > 0)
        dout.attrs['long_name'] = 'Total cloud area'
        dout.attrs['units'] = ds.FISCCP1_COSP.units
    elif vname.lower() == 'cllisccp':
        jhist = ds['FISCCP1_COSP']
        jhist = jhist.where((jhist.cosp_tau > 0.3) & (jhist.cosp_prs > 680))
        d = jhist.sum(dim=('cosp_tau', 'cosp_prs'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('cosp_tau', 'cosp_prs')) > 0)
        dout.attrs['long_name'] = 'Low-topped cloud area'
        dout.attrs['units'] = ds.FISCCP1_COSP.units
    elif vname.lower() == 'clmisccp':
        jhist = ds['FISCCP1_COSP']
        jhist = jhist.where((jhist.cosp_tau > 0.3) & (jhist.cosp_prs > 440) & (jhist.cosp_prs < 680))
        d = jhist.sum(dim=('cosp_tau', 'cosp_prs'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('cosp_tau', 'cosp_prs')) > 0)
        dout.attrs['long_name'] = 'Mid-topped cloud area'
        dout.attrs['units'] = ds.FISCCP1_COSP.units
    elif vname.lower() == 'clhisccp':
        jhist = ds['FISCCP1_COSP']
        jhist = jhist.where((jhist.cosp_tau > 0.3) & (jhist.cosp_prs < 440))
        d = jhist.sum(dim=('cosp_tau', 'cosp_prs'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('cosp_tau', 'cosp_prs')) > 0)
        dout.attrs['long_name'] = 'High-topped cloud area'
        dout.attrs['units'] = ds.FISCCP1_COSP.units
    else:
        raise NameError('Variable %s not found'%(vname))
    
    return dout


def get_datetimes(ds):
    import pandas
    dates = ds.date
    datesecs = ds.datesec
    hours = datesecs / 3600
    fulldates = ['%i%02i'%(d, h) for (d, h) in zip(dates, hours)]
    return pandas.to_datetime(fulldates, format='%Y%m%d%H')
