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
                                 fraction=0.05)
            return pl

        anim = animation.FuncAnimation(figure, plotstep,
                                       frames=ds.time.size,
                                       init_func=init)
        anim.save(outputfile)


if __name__ == '__main__':
    import plac; plac.call(main)
