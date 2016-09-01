#!/usr/bin/env python3

def main(inputfile, vname, outputfile, projection='robin'):
    import numpy, xarray
    import matplotlib; matplotlib.use('Agg')
    from matplotlib import pyplot, animation
    from mpl_toolkits.basemap import Basemap
    import seaborn

    # make plot using matplotlib tricontour function
    with xarray.open_dataset(inputfile, decode_times=False) as ds:

        # select data;
        # TODO: add code to interpolate to a few set levels and plot
        # each level
        data = ds[vname]
        if 'lev' in data.dims:
            print('Warning: data have multiple levels; selecting level 0')
            #data = get_var_at_plev(ds, vname, 200)
            data = data.isel(lev=0)

        # setup figure
        figure, ax = pyplot.subplots()

        # setup map
        m = Basemap(projection=projection, lon_0=180)
        x, y = m(ds.lon.values, ds.lat.values)
        m.drawcoastlines()

        # select levels and colormaps
        vmin = data.min().values
        vmax = data.max().values
        if vmin < 0 and vmax > 0:
            vmax = max(numpy.abs(vmin), numpy.abs(vmax))
            vmin = -vmax
            cmap = pyplot.get_cmap('RdBu_r')
        else:
            cmap = pyplot.get_cmap('plasma')

        # define animation functions
        def plotstep(i):
            pl = m.contourf(x, y, data.isel(time=i).squeeze(),
                            tri=True, cmap=cmap,
                            levels=numpy.linspace(vmin, vmax, 11),
                            extend='both')
            ax.set_title('%s; time = %i'%(ds.case, i))
            return pl

        def init():
            pl = plotstep(0)
            cb = pyplot.colorbar(pl, orientation='horizontal',
                                 label='%s (%s)'%(data.long_name, data.units),
                                 fraction=0.05, pad=0.02)
            return pl

        anim = animation.FuncAnimation(figure, plotstep,
                                       frames=ds.time.size,
                                       init_func=init)
        anim.save(outputfile)


def get_var_at_plev(ds, vname, plev):
    import nclpy
    vname_plev = '%s%0f'%(vname, plev)
    if vname_plev in ds:
        return ds[vname_plev]
    else:
        # Interpolate to pressure level
        vint = nclpy.vinth2p(
            ds[vname].transpose('time', 'ncol', 'lev'), ds.hyam, ds.hybm, 
            1e-2 * ds.P0, ds.PS, numpy.array([plev,]),
        )
        
        vint = xarray.DataArray(
            vint, dims=('time', 'ncol', 'plev'), coords={'time': ds.time},
            attrs={'long_name': '%.0f hPa %s'%(plev, ds[vname].long_name.lower()), 'units': ds[vname].units}
        )
        
        # add to dataset
        ds.update({vname_plev: vint})
        
        return vint
    
def get_var(ds, vname):
    if vname == 'U850':
        return get_var_at_plev(ds, 'U', 850)
    elif vname == 'U500':
        return get_var_at_plev(ds, 'U', 500)
    elif vname == 'U250':
        return get_var_at_plev(ds, 'U', 250)
    if vname == 'V850':
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


if __name__ == '__main__':
    import plac; plac.call(main)
