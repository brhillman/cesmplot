#!/usr/bin/env python3

def main(inputfile, vname, outputfile=None, projection='robin'):
    import numpy, xarray
    from matplotlib import pyplot
    from mpl_toolkits.basemap import Basemap
    import seaborn

    with xarray.open_dataset(inputfile, decode_times=False) as ds:

        # setup axes
        figure, ax = pyplot.subplots()

        # setup map
        m = Basemap(projection=projection, lon_0=180)
        x, y = m(ds.lon.values, ds.lat.values)
        m.drawcoastlines()

        # select data
        data = ds[vname]
        if 'lev' in data.dims:
            print('Warning: selecting lev=0')
            data = data.isel(lev=0)

        if 'time' in data.dims:
            print('Warning: calculating time average')
            data = data.mean('time', keep_attrs=True)

        # make plot
        vmin = data.min().values
        vmax = data.max().values
        if vmin < 0 and vmax > 0:
            vmin = min(-vmin.abs(), -vmax.abs())
            vmax = max(vmin.abs(), vmax.abs())
            cmap = pyplot.get_cmap('RdBu_r')
        else:
            cmap = pyplot.get_cmap('plasma')

        pl = m.contourf(x, y, data, tri=True, cmap=cmap,
                        levels=numpy.linspace(vmin, vmax, 11))

        cb = pyplot.colorbar(pl, orientation='horizontal', fraction=0.05,
                             label='%s (%s)'%(data.long_name, data.units))

        # calculate statistics
        # TODO: make weighted statistics
        weights = (ds.lat * numpy.pi / 180.0) * data / data
        global_mean = data.mean() #(data * weights).sum() / weights.sum()
        global_stddev = data.std()

        # label plot
        ax.set_title('mean = %.1f; stddev = %.1f'%(global_mean, global_stddev))

        # save figure
        if outputfile is not None:
            figure.savefig(outputfile, format='pdf')
        else:
            figure.show()


if __name__ == '__main__':
    import plac; plac.call(main)
