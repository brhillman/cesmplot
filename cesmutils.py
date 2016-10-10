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
        dout = dout.rename({'cosp_tau': 'tau', 'cosp_htmisr': 'cth'})
    elif vname.lower() == 'cltmisr':
        jhist = get_var(ds, 'clmisr') #ds['CLD_MISR']
        jhist = jhist.where(jhist.tau > 0.3)
        d = jhist.sum(dim=('tau', 'cth'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('tau', 'cth')) > 0)
        dout.attrs['long_name'] = 'Total cloud area'
        dout.attrs['units'] = get_var(ds, 'clmisr').attrs['units']
    elif vname.lower() == 'cllmisr':
        jhist = get_var(ds, 'clmisr') #ds['CLD_MISR']
        jhist = jhist.where((jhist.tau > 0.3) & (jhist.cth > 0) & (jhist.cth < 3))
        d = jhist.sum(dim=('tau', 'cth'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('tau', 'cth')) > 0)
        dout.attrs['long_name'] = 'Low-topped cloud area'
        dout.attrs['units'] = get_var(ds, 'clmisr').attrs['units']
    elif vname.lower() == 'clmmisr':
        jhist = get_var(ds, 'clmisr') #ds['CLD_MISR']
        jhist = jhist.where((jhist.tau > 0.3) & (jhist.cth > 3) & (jhist.cth < 7))
        d = jhist.sum(dim=('tau', 'cth'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('tau', 'cth')) > 0)
        dout.attrs['long_name'] = 'Mid-topped cloud area'
        dout.attrs['units'] = get_var(ds, 'clmisr').attrs['units']
    elif vname.lower() == 'clhmisr':
        jhist = get_var(ds, 'clmisr') #ds['CLD_MISR']
        jhist = jhist.where((jhist.tau > 0.3) & (jhist.cth > 7))
        d = jhist.sum(dim=('tau', 'cth'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('tau', 'cth')) > 0)
        dout.attrs['long_name'] = 'High-topped cloud area'
        dout.attrs['units'] = get_var(ds, 'clmisr').attrs['units']
    elif vname.lower() == 'clisccp':
        dout = ds['FISCCP1_COSP']
        dout = dout.rename({'cosp_tau': 'tau', 'cosp_prs': 'plev'})
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
    # MODIS fields from COSP
    elif vname.lower() == 'clmodis':
        dout = ds['CLMODIS']
        dout = dout.rename({'cosp_tau_modis': 'tau', 'cosp_prs': 'plev'})
    elif vname.lower() == 'cltmodis':
        jhist = get_var(ds, 'clmodis')
        jhist = jhist.where(jhist.tau > 0.3)
        d = jhist.sum(dim=('tau', 'plev'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('tau', 'plev')) > 0)
        dout.attrs['long_name'] = 'Total cloud area'
        dout.attrs['units'] = ds.CLMODIS.units
    elif vname.lower() == 'cllmodis':
        jhist = get_var(ds, 'clmodis')
        jhist = jhist.where((jhist.tau > 0.3) & (jhist.plev > 680))
        d = jhist.sum(dim=('tau', 'plev'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('tau', 'plev')) > 0)
        dout.attrs['long_name'] = 'Low-topped cloud area'
        dout.attrs['units'] = ds.CLMODIS.units
    elif vname.lower() == 'clmmodis':
        jhist = get_var(ds, 'clmodis')
        jhist = jhist.where((jhist.tau > 0.3) & (jhist.plev > 440) & (jhist.plev < 680))
        d = jhist.sum(dim=('tau', 'plev'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('tau', 'plev')) > 0)
        dout.attrs['long_name'] = 'Mid-topped cloud area'
        dout.attrs['units'] = ds.CLMODIS.units
    elif vname.lower() == 'clhmodis':
        jhist = get_var(ds, 'clmodis')
        jhist = jhist.where((jhist.tau > 0.3) & (jhist.plev < 440))
        d = jhist.sum(dim=('tau', 'plev'), keep_attrs=True)
        dout = d.where(jhist.notnull().sum(dim=('tau', 'plev')) > 0)
        dout.attrs['long_name'] = 'High-topped cloud area'
        dout.attrs['units'] = ds.CLMODIS.units
    elif vname.lower() == 'climodis':
        dout = ds['CLIMODIS']
    elif vname.lower() == 'clwmodis':
        dout = ds['CLWMODIS']
    elif vname.lower() == 'iwpmodis':
        # Weighted by cloud amount in CAM run, need to divide here
        d = ds['IWPMODIS']
        w = ds['CLIMODIS']
        dout = d / w
        dout.attrs = d.attrs
    elif vname.lower() == 'lwpmodis':
        # Weighted by cloud amount in CAM run, need to divide here
        d = ds['LWPMODIS']
        w = ds['CLWMODIS']
        dout = d / w
        dout.attrs = d.attrs
    elif vname.lower() == 'pctmodis':
        # Weighted by cloud amount in CAM run, need to divide here
        d = ds['PCTMODIS']
        w = ds['CLTMODIS']
        dout = d / w
        dout.attrs = d.attrs
        dout.attrs['long_name'] = 'MODIS-sim cloud top pressure'
    elif vname.lower() == 'reffclimodis':
        # Weighted by cloud amount in CAM run, need to divide here
        d = ds['REFFCLIMODIS']
        w = ds['CLIMODIS']
        dout = d / w
        dout.attrs = d.attrs
        dout.attrs['long_name'] = 'MODIS-sim cloud ice effective radius'
    elif vname.lower() == 'reffclwmodis':
        # Weighted by cloud amount in CAM run, need to divide here
        d = ds['REFFCLWMODIS']
        w = ds['CLWMODIS']
        dout = d / w
        dout.attrs = d.attrs
        dout.attrs['long_name'] = 'MODIS-sim cloud liquid effective radius'
    elif vname.lower() == 'tauilogmodis':
        # Weighted by cloud amount in CAM run, need to divide here
        d = ds['TAUILOGMODIS']
        w = ds['CLIMODIS']
        dout = 10 ** (d / w)
        dout.attrs = d.attrs
        dout.attrs['long_name'] = 'MODIS-sim log-mean ice cloud optical depth'
    elif vname.lower() == 'tauwlogmodis':
        # Weighted by cloud amount in CAM run, need to divide here
        d = ds['TAUWLOGMODIS']
        w = ds['CLWMODIS']
        dout = 10 ** (d / w)
        dout.attrs = d.attrs
        dout.attrs['long_name'] = 'MODIS-sim log-mean liquid cloud optical depth'
    elif vname.lower() == 'tautlogmodis':
        # Weighted by cloud amount in CAM run, need to divide here
        d = ds['TAUTLOGMODIS']
        w = ds['CLTMODIS']
        dout = 10 ** (d / w)
        dout.attrs = d.attrs
        dout.attrs['long_name'] = 'MODIS-sim log-mean total cloud optical depth'
    elif vname.lower() == 'tauimodis':
        # Weighted by cloud amount in CAM run, need to divide here
        d = ds['TAUIMODIS']
        w = ds['CLIMODIS']
        dout = d / w
        dout.attrs = d.attrs
        dout.attrs['long_name'] = 'MODIS-sim linear-mean ice cloud optical depth'
    elif vname.lower() == 'tauwmodis':
        # Weighted by cloud amount in CAM run, need to divide here
        d = ds['TAUWMODIS']
        w = ds['CLWMODIS']
        dout = d / w
        dout.attrs = d.attrs
        dout.attrs['long_name'] = 'MODIS-sim linear-mean liquid cloud optical depth'
    elif vname.lower() == 'tautmodis':
        # Weighted by cloud amount in CAM run, need to divide here
        d = ds['TAUTMODIS']
        w = ds['CLTMODIS']
        dout = d / w
        dout.attrs = d.attrs
        dout.attrs['long_name'] = 'MODIS-sim linear-mean total cloud optical depth'
    # CloudSat fields from COSP
    elif vname.lower() == 'cfaddbze94':
        d = 100.0 * ds['CFAD_DBZE94_CS']
        dout = d.rename({'cosp_dbze': 'dbze', 'cosp_ht': 'alt40'})
        dout.attrs = ds['CFAD_DBZE94_CS'].attrs
    else:
        raise NameError('Variable %s not found'%(vname))

    dout.name = vname

    # fix units
    if 'units' in dout.attrs:
        if dout.attrs['units'] == 'percent': 
            dout.attrs['units'] = '%'
        elif dout.attrs['units'] == 'fraction':
            dout[:] = 100.0 * dout
            dout.attrs['units'] = '%'
    
    return dout


def get_datetimes(ds):
    import pandas
    dates = ds.date
    datesecs = ds.datesec
    hours = datesecs / 3600
    fulldates = ['%08i%02i'%(d, h) for (d, h) in zip(dates, hours)]
    return pandas.to_datetime(fulldates, format='%Y%m%d%H')
