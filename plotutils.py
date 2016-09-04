def plotmap(lon, lat, data, projection='robin', **kw_args):
    if 'ncol' in data.dims:
        return plotmap_unstructured(lon, lat, data, projection=projection, 
                                    **kw_args)
                                    
    else:
        return plotmap_lonlat(lon, lat, data, projection=projection,
                              **kw_args)


def plotmap_lonlat(lon, lat, data, projection='robin', **kw_args):
    import numpy
    from matplotlib import pyplot
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
    import numpy
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
