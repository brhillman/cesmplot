def plotmap(lon, lat, data, ax=None, **kw_args):
    import numpy
    from matplotlib.tri import Triangulation
    from mpl_toolkits.basemap import Basemap
    
    # set up the map
    m = Basemap(projection='robin', lon_0=0)
    x, y = m(lon.values, lat.values)

    # dress up the map
    m.drawcoastlines()

    # check if we have unstructured data; if so, tri=True
    # TODO: fix this...just assume tri is true for now...

    # might have missing data...that's a problem for tricontourf so
    # we need to set the mask ourselves. To do that, first set up the
    # triangulation
    triangulation = Triangulation(x, y)

    # then need to get the mask in the triangulation grid
    mask = numpy.any(numpy.isnan(data.values)[triangulation.triangles], axis=1)
    
    # now we can contour, but pass in the pre-computed triangulation
    return m.contourf(x, y, data, tri=True,
                      triangles=triangulation.triangles, mask=mask, **kw_args)

