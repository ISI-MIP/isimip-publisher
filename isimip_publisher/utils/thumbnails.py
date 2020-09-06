import logging
import shutil
from pathlib import Path

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from netCDF4 import Dataset

from ..config import settings

logger = logging.getLogger(__name__)

WIDTH = 800
HEIGHT = 380
DPI = 96
LEVELS = 10


def write_thumbnail_file(abspath, output_abspath=None):
    if not output_abspath:
        output_abspath = Path(abspath).with_suffix('.png')

    logger.info('write_file_thumbnail %s', output_abspath)

    try:
        with Dataset(abspath, mode='r') as dataset:
            # find the variable with the most dimensions
            variable = sorted(dataset.variables.values(), key=lambda variable: variable.ndim)[-1]

            if not settings.MOCK and variable.ndim in [3, 4, 5, 6]:
                try:
                    lat = dataset.variables['lat'][:]
                    lon = dataset.variables['lon'][:]

                    if variable.ndim == 3:
                        var = variable[0, :, :]
                    elif variable.ndim == 4:
                        var = variable[0, 0, :, :]
                    elif variable.ndim == 5:
                        var = variable[0, 0, 0, :, :]
                    else:
                        var = variable[0, 0, 0, 0, :, :]

                    plt.clf()
                    plt.axes(projection=ccrs.PlateCarree()).coastlines()
                    plt.contourf(lon, lat, var, LEVELS, transform=ccrs.PlateCarree())
                    plt.title(variable.name)

                    fig = plt.gcf()
                    fig.set_size_inches(WIDTH/DPI, HEIGHT/DPI)
                    fig.savefig(output_abspath, dpi=DPI)

                    return
                except (IndexError, ValueError, TypeError) as e:
                    logger.warn(e)
    except OSError:
        pass

    # if plotting did not work, copy empty.png
    empty_file = Path(__file__).parent.parent / 'extras' / 'empty.png'
    shutil.copyfile(empty_file, output_abspath)
