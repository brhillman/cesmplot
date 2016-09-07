#!/usr/bin/env python3
import os, sys
import numpy, xarray
import matplotlib; matplotlib.use('Agg')
from matplotlib import pyplot
import plotutils, cesmutils
import seaborn; seaborn.set(style='white')

# TODO: add option to just pick off a single time?
def main(inputfile, outputdir):
    # make sure output directory exists
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    mapvars = ('cltmisr', 'cllmisr', 'clmmisr', 'clhmisr', 
               'cltisccp', 'cllisccp', 'clmisccp', 'clhisccp',
               'cltmodis', 'cllmodis', 'clmmodis', 'clhmodis',
               'clwmodis', 'climodis', 'iwpmodis', 'lwpmodis', 'pctmodis',
               'tautlogmodis', 'tauwlogmodis', 'tauilogmodis',
               'tautmodis', 'tauwmodis', 'tauimodis',
               'reffclwmodis', 'reffclimodis',
               'CLDTOT_CS', 'CLDTOT_CS2', 
               'CLDTOT_CAL', 'CLDLOW_CAL', 'CLDMED_CAL', 'CLDHGH_CAL')

    histvars = ('clmodis', 'clmisr', 'clisccp', 'cfadDbze94')

    region_bnds = {'Global': (-numpy.inf, numpy.inf, -numpy.inf, numpy.inf),
                   'Tropics': (-numpy.inf, numpy.inf, -20.0, 20.0),
                   'Arctic': (-numpy.inf, numpy.inf, 75.0, numpy.inf),
                   'Antarctic': (-numpy.inf, numpy.inf, -numpy.inf, -75.0)}
 
    # open file
    print('Open file ', inputfile)
    with xarray.open_dataset(inputfile, decode_times=False) as ds:

        # calculate time-average
        if 'time' in ds.dims and len(ds.time) > 1:
            print('Calculate time-average...')
            ds = ds.mean('time', keep_attrs=True).squeeze()
        else:
            ds = ds.squeeze()

        # get case name
        cn = ds.case

        # plot joint histograms
        print('Plot 2D joint histograms...')
        for vn in histvars:
            for region in region_bnds.keys():
                print('Plotting variable %s, region %s'%(vn, region))

                # get data
                d = cesmutils.get_var(ds, vn)

                # mask data outside region
                lon1, lon2, lat1, lat2 = region_bnds[region]
                dm = d.where((ds.lon > lon1) & (ds.lon <= lon2) & 
                            (ds.lat > lat1) & (ds.lat <= lat2))

                # calculate weighted average
                w = numpy.cos(numpy.pi * ds.lat / 180.0)
                *__, w = xarray.broadcast(dm, w)
                w = w.where(dm.notnull())
                dm = (dm * w).sum('ncol') / w.sum('ncol')

                # copy attributes
                dm.attrs = d.attrs
                dm.name = d.name
                d = dm

                figure, ax = pyplot.subplots()
                if vn == 'cfadDbze94':
                    vmin = 0; vmax = 0.1
                else:
                    vmin = None; vmax = None
                pl = plotutils.plot_jointhist(d, )#vmin=vmin, vmax=vmax)

                # add a colorbar
                cb = pyplot.colorbar(pl, orientation='vertical',
                                     label='%s (%s)'%(d.long_name, d.units))

                # label plot
                ax.set_title('%s %s'%(cn, region))

                # put cloud fraction on plot
                if 'tau' in d.dims:
                    cf = d.where(d.tau > 0.3).sum()
                    label = r'$\mathregular{C_{\tau > 0.3} = %.1f}$'%cf.values
                    ax.text(0.99, 0.99, label,
                            transform=ax.transAxes,
                            ha='right', va='top')

                figname = '%s/%s.%s.%s'%(outputdir, vn, cn, region)
                figure.savefig(figname + '.pdf', format='pdf', bbox_inches='tight')
                pyplot.close(figure)

        # plot fields
        print('Plot 2D maps...')
        for vn in mapvars:
            print('Plotting variable %s...'%(vn)); sys.stdout.flush()

            # get data from file (possibly derived)
            d = cesmutils.get_var(ds, vn)
            x = ds.lon
            y = ds.lat

            # plot data
            figure, ax = pyplot.subplots()
            pl = plotutils.plotmap(
                x, y, d, cmap='plasma',
                levels=numpy.linspace(d.min().values, d.max().values, 21), 
                extend='both'
            )

            # label
            ax.set_title('%s (mean = %.1f)'%(
                         ds.case, cesmutils.area_average(d, y)))

            # add colorbar
            pyplot.colorbar(pl, orientation='horizontal', 
                            label='%s (%s)'%(d.long_name, d.units),
                            pad=0.01)

            # save figure
            figname = '%s/%s.%s'%(outputdir, vn, cn)
            figure.savefig(figname + '.pdf', format='pdf', bbox_inches='tight')
            pyplot.close(figure)


if __name__ == '__main__':
    import plac; plac.call(main)
