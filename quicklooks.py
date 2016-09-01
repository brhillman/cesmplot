#!/usr/bin/env python3
# TODO: add option to just pick off a single time?
def main(inputfiles, outputdir):
    import os, sys
    import numpy, xarray
    import matplotlib; matplotlib.use('Agg')
    from matplotlib import pyplot
    import plotutils
    import seaborn

    # make sure output directory exists
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    varnames = ('cltmisr', 'cllmisr', 'clmmisr', 'clhmisr', 'CLDTOT')
                #'cltisccp', 'cllisccp', 'clmisccp', 'clhisccp',
                #'cltmodis', 'cllmodis', 'clmmodis', 'clhmodis')

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
            d = get_var(ds, vn)
            x = ds.lon
            y = ds.lat

            # plot data
            figure, ax = pyplot.subplots()
            pl = plotutils.plotmap(
                x, y, d, cmap='plasma',
                levels=numpy.linspace(d.min().values, d.max().values, 11), 
                extend='both'
            )

            # add colorbar
            pyplot.colorbar(pl, orientation='horizontal', 
                            label='%s (%s)'%(d.long_name, d.units))

            # save figure
            figname = '%s/%s.%s'%(outputdir, vn, cn)
            figure.savefig(figname + '.pdf', format='pdf', bbox_inches='tight')


def get_var(ds, vname):
    if vname in ds.variables.keys():
        d = ds[vname]
    elif vname == 'cltmisr':
        jhist = ds['CLD_MISR']
        jhist = jhist.where(jhist.cosp_tau > 0.3)
        d = jhist.sum(dim=('cosp_tau', 'cosp_htmisr'), keep_attrs=True)
        d = d.where(jhist.notnull().sum(dim=('cosp_tau', 'cosp_htmisr')) > 0)
        d.attrs['long_name'] = 'Total cloud area'
        d.attrs['units'] = ds.CLD_MISR.units
    elif vname == 'cllmisr':
        jhist = ds['CLD_MISR']
        jhist = jhist.where((jhist.cosp_tau > 0.3) & (jhist.cosp_htmisr > 0) & (jhist.cosp_htmisr < 3))
        d = jhist.sum(dim=('cosp_tau', 'cosp_htmisr'), keep_attrs=True)
        d = d.where(jhist.notnull().sum(dim=('cosp_tau', 'cosp_htmisr')) > 0)
        d.attrs['long_name'] = 'Low-topped cloud area'
        d.attrs['units'] = ds.CLD_MISR.units
    elif vname == 'clmmisr':
        jhist = ds['CLD_MISR']
        jhist = jhist.where((jhist.cosp_tau > 0.3) & (jhist.cosp_htmisr > 3) & (jhist.cosp_htmisr < 7))
        d = jhist.sum(dim=('cosp_tau', 'cosp_htmisr'), keep_attrs=True)
        d = d.where(jhist.notnull().sum(dim=('cosp_tau', 'cosp_htmisr')) > 0)
        d.attrs['long_name'] = 'Mid-topped cloud area'
        d.attrs['units'] = ds.CLD_MISR.units
    elif vname == 'clhmisr':
        jhist = ds['CLD_MISR']
        jhist = jhist.where((jhist.cosp_tau > 0.3) & (jhist.cosp_htmisr > 7))
        d = jhist.sum(dim=('cosp_tau', 'cosp_htmisr'), keep_attrs=True)
        d = d.where(jhist.notnull().sum(dim=('cosp_tau', 'cosp_htmisr')) > 0)
        d.attrs['long_name'] = 'High-topped cloud area'
        d.attrs['units'] = ds.CLD_MISR.units
    else:
        raise NameError(vname + ' not found.')
    return d


if __name__ == '__main__':
    import plac; plac.call(main)
