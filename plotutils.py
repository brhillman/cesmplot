#!/usr/bin/env python3

import numpy
from matplotlib import pyplot

cmap_full = 'bone_r'
cmap_diff = 'RdBu_r'

clevels = {'cfadDbze94': numpy.linspace(0, 0.1, 21),
           'clmisr': numpy.linspace(0, 10, 21),
           'clisccp': numpy.linspace(0, 10, 21),
           'clmodis': numpy.linspace(0, 10, 21)}
dlevels = {'cfdaDbze94': numpy.linspace(-0.05, 0.05)}


def plotmap(lon, lat, data, projection='robin', **kw_args):
    if 'ncol' in data.dims:
        return plotmap_unstructured(lon, lat, data, projection=projection, 
                                    **kw_args)
    else:
        return plotmap_lonlat(lon, lat, data, projection=projection,
                              **kw_args)


def plotmap_lonlat(lon, lat, data, projection='robin', **kw_args):
    from mpl_toolkits.basemap import Basemap

    # set up the map
    m = Basemap(projection=projection, lon_0=0)
    lonm, latm = numpy.meshgrid(lon.values, lat.values, indexing='ij')
    x, y = m(lonm, latm)

    # draw coastlines
    m.drawcoastlines()

    # return contour plot
    return m.contourf(x, y, data, **kw_args)


def plotmap_unstructured(lon, lat, data, projection='robin', **kw_args):
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


def plot_jointhist(data, **kwargs):

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

    # make plot
    print(data.name)
    if data.min() < 0 and data.max() > 0:
        if data.name in dlevels.keys():
            vmin = dlevels[data.name][0]
            vmax = dlevels[data.name][-1]
        else:
            vmax = max(abs(data.min()), abs(data.max()))
            vmin = -vmax
        cmap = cmap_diff
    else:
        if data.name in clevels.keys():
            vmin = clevels[data.name][0]
            vmax = clevels[data.name][-1]
        else:
            vmin = data.min().values
            vmax = data.max().values
        cmap = cmap_full

    pl = ax.pcolor(data.transpose(ydim, xdim), 
                   vmin=vmin, vmax=vmax,
                   cmap=cmap, **kwargs)

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
