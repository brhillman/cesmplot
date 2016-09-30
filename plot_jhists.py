#!/usr/bin/env python3

import numpy, xarray
import matplotlib; matplotlib.use('Agg')
from matplotlib import pyplot
import seaborn; seaborn.set(style='white')
from cesmutils import get_var

def read_data(inputfile):
    ds = xarray.open_dataset(inputfile, decode_times=False)
    
    if 'time' in ds.dims:
        if len(ds.time) > 1:
            print('Warning: calculating time average')
            ds = ds.mean('time', keep_attrs=True)
        else:
            ds = ds.squeeze()

    return ds


def plot_jhist(data, **kwargs):

    # get x-dim name
    if 'tau' in data.dims:
        xdim = 'tau'
    elif 'dbze' in data.dims:
        xdim = 'dbze'
    else:
        raise ValueError('No valid x-dim found.')

    # get y-dim name
    if 'plev' in data.dims:
        ydim = 'plev'
    elif 'cth' in data.dims:
        ydim = 'cth'
    elif 'alt40' in data.dims:
        ydim = 'alt40'
    else:
        raise ValueError('No valid y-dim found.')

    # get axes handle
    ax = pyplot.gca()
    pl = ax.pcolor(data.transpose(ydim, xdim), **kwargs)

    # manually set axes tick labels
    xticks = [i + 0.5 for i in range(data[xdim].size)]
    xticklabels = ['%.1f'%(x) for x in data[xdim].values]
    if len(xticks) < 10:
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)
    else:
        ax.set_xticks(xticks[::2])
        ax.set_xticklabels(xticklabels[::2])

    yticks = [i + 0.5 for i in range(data[ydim].size)]
    yticklabels = ['%.1f'%(y) for y in data[ydim].values]
    if len(yticks) < 10:
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels)
    else:
        ax.set_yticks(yticks[::2])
        ax.set_yticklabels(yticklabels[::2])

    ax.set_xlabel(data[xdim].long_name)
    ax.set_ylabel(data[ydim].long_name)

    return pl
def main(nrows: ('number of rows', 'option', None, int), 
         ncols: ('number of columns', 'option', None, int), 
         vname, outputfile, *inputfiles):

    # open datasets
    datasets = [read_data(f) for f in inputfiles]

    # get data; use cesm convenience function
    dataarrays = [get_var(ds, vname).squeeze() for ds in datasets]

    dataarrays = [da.sel(dbze=slice(-27.5, None))
                  if 'dbze' in da.dims else da for da in dataarrays]


    # get data limits
    vmin = min([d.min().values for d in dataarrays])
    vmax = max([d.max().values for d in dataarrays])

    # setup axes
    if nrows is None: nrows = 1
    if ncols is None: ncols = len(inputfiles)
    figure, axes = pyplot.subplots(nrows, ncols)

    for icase, (ds, da) in enumerate(zip(datasets, dataarrays)):

        # if data spans zero, then set data limits to symmetrically span zero
        # and select a divergent colormap. Otherwise keep data limits and
        # select a sequential colormap
        if vmin < 0 and vmax > 0:
            vmax = max(vmin.abs(), vmax.abs())
            vmin = -vmax
            cmap = pyplot.get_cmap('RdBu_r')
        else:
            cmap = pyplot.get_cmap('bone_r')

        ax = figure.add_axes(numpy.atleast_1d(axes).ravel()[icase])
        pl = plot_jhist(da, cmap=cmap, vmin=vmin, vmax=vmax)

        # calculate statistics
        # TODO: make weighted statistics
        #weights = (ds.lat * numpy.pi / 180.0) * data / data
        #global_mean = (data * weights).sum() / weights.sum()

        # label plot
        #ax.set_title('%s (%.1f)'%(ds.case, global_mean))
        ax.set_title(ds.case)

    cb = pyplot.colorbar(pl, ax=numpy.atleast_1d(axes).ravel().tolist(),
                         orientation='vertical', 
                         fraction=0.05, pad=0.02,
                         label='%s (%s)'%(da.long_name, da.units))

    if len(numpy.atleast_1d(axes)) > 1:
        for ax in axes[1:]:
            ax.set_yticklabels('')
            ax.set_ylabel('')

    # save figure
    figure.savefig(outputfile, bbox_inches='tight')


if __name__ == '__main__':
    import plac; plac.call(main)
