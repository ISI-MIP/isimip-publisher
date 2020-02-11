import logging
import os
import shutil

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from netCDF4 import Dataset

logger = logging.getLogger(__name__)

WIDTH = 800
HEIGHT = 380
DPI = 96
LEVELS = 10


def write_dataset_thumbnail(dataset_abspath, files):
    write_file_thumbnail(files[-1], output_abspath='%s.png' % dataset_abspath)


def write_file_thumbnail(file_abspath, output_abspath=None):
    mock = os.environ.get('MOCK', '').lower() in ['t', 'true', 1]

    if not output_abspath:
        output_abspath = file_abspath.replace('.nc4', '.png')

    with Dataset(file_abspath, mode='r') as dataset:

        for var_name, variable in dataset.variables.items():
            if len(variable.dimensions) > 1:
                break

        if not mock:
            try:
                lat = dataset.variables['lat'][:]
                lon = dataset.variables['lon'][:]
                var = dataset.variables[var_name][1, :, :]

                plt.clf()
                plt.axes(projection=ccrs.PlateCarree()).coastlines()
                plt.contourf(lon, lat, var, LEVELS, transform=ccrs.PlateCarree())
                plt.title(var_name)

                fig = plt.gcf()
                fig.set_size_inches(WIDTH/DPI, HEIGHT/DPI)
                fig.savefig(output_abspath, dpi=DPI)

                return
            except (IndexError, ValueError) as e:
                logger.warn(e)

        # if plotting did not work, copy empty.png
        empty_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'extras', 'empty.png')
        shutil.copyfile(empty_file, output_abspath)
