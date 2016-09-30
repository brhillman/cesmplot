#!/usr/bin/env python3

import numpy, xarray
import matplotlib; matplotlib.use('Agg')
from matplotlib import pyplot
import seaborn
import cesmutils

def plot_map(lon, lat, data, projection='robin', **kw_args):
    if 'ncol' in data.dims:
        return plot_map_unstructured(lon, lat, data, projection=projection, 
                                    **kw_args)
    else:
        return plot_map_lonlat(lon, lat, data, projection=projection,
                              **kw_args)


def fix_lon(da):
    """
    Function to make sure longitude coordinates go from -180 to 180,
    rather than from 0 to 360.
    """

    da['lon'].values = numpy.where(da.lon > 180, da.lon - 360, da.lon)
    da = da.roll(lon=180)
    return da


def plot_map_lonlat(lon, lat, data, projection='robin', **kw_args):
    from mpl_toolkits.basemap import Basemap

    # fix longitudes; we need them to go from -180 to 180
    data = fix_lon(data)
    lon = data.lon

    # set up the map
    m = Basemap(projection=projection, lon_0=0)
    lonm, latm = numpy.meshgrid(lon.values, lat.values, indexing='ij')
    x, y = m(lonm, latm)

    # draw coastlines
    m.drawcoastlines()

    # return contour plot
    return m.contourf(x, y, data.transpose('lon', 'lat'), **kw_args)


def plot_map_unstructured(lon, lat, data, projection='robin', **kw_args):
    from matplotlib.tri import Triangulation
    from mpl_toolkits.basemap import Basemap
    
    # set up the map
    m = Basemap(projection=projection, lon_0=0)
    x, y = m(lon.values, lat.values)

    # draw coastlines
    m.drawcoastlines()

    # might have missing data...that's a problem for tricontourf so
    # we need to set the mask ourselves. To do that, first set up the
    # triangulation
    triangulation = Triangulation(x, y)

    # then need to get the mask in the triangulation grid
    mask = numpy.any(numpy.isnan(data.values)[triangulation.triangles], axis=1)
    
    # now we can contour, but pass in the pre-computed triangulation
    return m.contourf(x, y, data, tri=True,
                      triangles=triangulation.triangles, mask=mask, **kw_args)



def read_data(inputfile):
    ds = xarray.open_dataset(inputfile, decode_times=False)
    
    if 'time' in ds.dims:
        if len(ds.time) > 1:
            print('Warning: calculating time average')
            ds = ds.mean('time', keep_attrs=True)
        else:
            ds = ds.squeeze()

    return ds


# Purpose: plot a single variable (or derived variable) from a CAM history
# file. This script depends on cesmutils.py to specify how to retrieve CAM 
# fields from CAM history files. cesmutils.py contains methods
# to calculate various derived fields.
def main(nrows: ('number of rows in figure', 'option', None, int), 
         ncols: ('number of columns in figure', 'option', None, int), 
         vname, outputfile, *inputfiles):

    # open datasets
    datasets = [read_data(f) for f in inputfiles]

    # get data; use cesm convenience function
    dataarrays = [cesmutils.get_var(ds, vname).squeeze() for ds in datasets]

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
            cmap = pyplot.get_cmap('plasma')

        ax = figure.add_axes(numpy.atleast_1d(axes).ravel()[icase])
        pl = plot_map(ds.lon, ds.lat, da, cmap=cmap, extend='both',
                               levels=numpy.linspace(vmin, vmax, 21))

        # calculate statistics
        # TODO: make weighted statistics
        #weights = (ds.lat * numpy.pi / 180.0) * data / data
        #global_mean = (data * weights).sum() / weights.sum()
        global_mean = da.mean() 
        global_stddev = da.std()

        # label plot
        ax.set_title('%s (%.1f)'%(ds.case, global_mean))

    cb = pyplot.colorbar(pl, ax=numpy.atleast_1d(axes).ravel().tolist(),
                         orientation='horizontal', 
                         fraction=0.05, pad=0.02,
                         label='%s (%s)'%(da.long_name, da.units))

    # save figure
    figure.savefig(outputfile, bbox_inches='tight')


if __name__ == '__main__':
    import plac; plac.call(main)
