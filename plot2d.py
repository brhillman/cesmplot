#!/usr/bin/env python3

# Purpose: plot a single variable (or derived variable) from a CAM history
# file. This script depends on plotutils.py to define the plotting routines
# for structured and unstructured grids, and on cesmutils.py to specify how
# to retrieve CAM fields from CAM history files. cesmutils.py contains methods
# to calculate various derived fields.
def main(inputfile, vname, outputfile=None, projection='robin'):
    import numpy, xarray
    import matplotlib; matplotlib.use('Agg')
    from matplotlib import pyplot
    import seaborn
    import plotutils, cesmutils

    with xarray.open_dataset(inputfile, decode_times=False) as ds:

        # setup axes
        figure, ax = pyplot.subplots(figsize=(5, 3))

        # get data; use cesm convenience function
        data = cesmutils.get_var(ds, vname)

        # make sure we don't still have a time dimension
        # TODO: if a time dimension exists; make a movie? Or add command line
        # options to decide how to handle this.
        if 'time' in data.dims:
            print('Warning: calculating time average')
            data = data.mean('time', keep_attrs=True)

        # figure out data limits
        vmin = data.min().values
        vmax = data.max().values

        # if data spans zero, then set data limits to symmetrically span zero
        # and select a divergent colormap. Otherwise keep data limits and
        # select a sequential colormap
        if vmin < 0 and vmax > 0:
            vmax = max(vmin.abs(), vmax.abs())
            vmin = -vmax
            cmap = pyplot.get_cmap('RdBu_r')
        else:
            cmap = pyplot.get_cmap('plasma')

        pl = plotutils.plotmap(ds.lon, ds.lat, data, cmap=cmap, extend='both',
                               levels=numpy.linspace(vmin, vmax, 21))

        cb = pyplot.colorbar(pl, orientation='horizontal', 
                             #fraction=0.05, pad=0.02,
                             label='%s (%s)'%(data.long_name, data.units))

        # calculate statistics
        # TODO: make weighted statistics
        #weights = (ds.lat * numpy.pi / 180.0) * data / data
        #global_mean = (data * weights).sum() / weights.sum()
        global_mean = data.mean() 
        global_stddev = data.std()

        # label plot
        ax.set_title('mean = %.1f; stddev = %.1f'%(global_mean, global_stddev))

        # save figure
        if outputfile is None:
            outputfile = '%s.%s.pdf'%(vname, ds.case)

        figure.savefig(outputfile, format='pdf', bbox_inches='tight')


if __name__ == '__main__':
    import plac; plac.call(main)
