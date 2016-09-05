#!/usr/bin/env python3

# TODO: add option to just pick off a single time?
def main(inputfiles, outputdir):
    import os, sys
    import numpy, xarray
    import matplotlib; matplotlib.use('Agg')
    from matplotlib import pyplot
    import plotutils, cesmutils
    import seaborn

    # make sure output directory exists
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    varnames = ('cltmisr', 'cllmisr', 'clmmisr', 'clhmisr', 
                'cltisccp', 'cllisccp', 'clmisccp', 'clhisccp',
                'cltmodis', 'cllmodis', 'clmmodis', 'clhmodis',
                'clwmodis', 'climodis', 'iwpmodis', 'lwpmodis', 'pctmodis',
                'tautlogmodis', 'tauwlogmodis', 'tauilogmodis',
                'tautmodis', 'tauwmodis', 'tauimodis',
                'reffclwmodis', 'reffclimodis',
                #'CLDTOT_CS', 'CLDTOT_CS2', 
                'CLDTOT_CAL', 'CLDLOW_CAL', 'CLDMED_CAL', 'CLDHGH_CAL')

    # open files into a multi-file dataset
    print('Open files ', inputfiles)
    with xarray.open_dataset(inputfiles, decode_times=False) as ds:

        # calculate time-average
        print('Calculate time-average...')
        ds = ds.mean('time', keep_attrs=True).squeeze()

        # get case name
        cn = ds.case

        # plot fields
        print('Plot 2D maps...')
        for vn in varnames:
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

            # add colorbar
            pyplot.colorbar(pl, orientation='horizontal', 
                            label='%s (%s)'%(d.long_name, d.units))

            # save figure
            figname = '%s/%s.%s'%(outputdir, vn, cn)
            figure.savefig(figname + '.pdf', format='pdf', bbox_inches='tight')
            pyplot.close(figure)


if __name__ == '__main__':
    import plac; plac.call(main)
