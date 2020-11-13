import logging
import shutil
from pathlib import Path

import cartopy.crs as ccrs
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from netCDF4 import Dataset

from ..config import settings

logger = logging.getLogger(__name__)

WIDTH = 800
HEIGHT = 440
DPI = 96
LEVELS = 10


def write_thumbnail_file(abspath, region=None, output_abspath=None):
    if not output_abspath:
        output_abspath = Path(abspath).with_suffix('.png')

    logger.info('write_file_thumbnail %s', output_abspath)

    if region is None:
        write_contour_plot(abspath, output_abspath)
    else:
        write_region_plot(region, output_abspath)


def write_region_plot(region, output_abspath):
    plt.clf()

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.set_global()

    lat, lon = region.get('lat'), region.get('lon')
    if None not in [lat, lon]:
        plt.plot([lon], [lat], color='#FABB53', linestyle='', alpha=0.75,
                 marker='*', markersize=20, markeredgewidth=1, markeredgecolor='#000000',
                 transform=ccrs.PlateCarree())

    north, east, south, west = region.get('north'), region.get('east'), region.get('south'), region.get('west')
    if None not in [north, east, south, west]:
        height = north - south
        width = east - west
        ax.add_patch(patches.Rectangle(xy=[west, south], width=width, height=height,
                                       edgecolor='#000000', facecolor='#FABB53', alpha=0.75, transform=ccrs.PlateCarree()))

    plt.title('Region')
    plt.subplots_adjust(left=40 / WIDTH, right=1 - 40 / WIDTH, bottom=40 / HEIGHT, top=1 - 40 / HEIGHT)

    fig = plt.gcf()
    fig.set_size_inches(WIDTH/DPI, HEIGHT/DPI)
    fig.savefig(output_abspath, dpi=DPI)


def write_contour_plot(dataset_abspath, output_abspath):
    if not settings.MOCK:
        try:
            with Dataset(dataset_abspath, mode='r') as dataset:
                # get lat and lon
                try:
                    # get lat and lon and the variable with the most dimensions
                    lat = dataset.variables['lat'][:]
                    lon = dataset.variables['lon'][:]
                    variable = sorted(dataset.variables.values(), key=lambda variable: variable.ndim)[-1]
                except (IndexError, ValueError, TypeError) as e:
                    logger.warn(e)
                else:
                    # create a contour plot
                    if variable.ndim in [3, 4, 5, 6]:
                        try:
                            if variable.ndim == 3:
                                var = variable[0, :, :]
                            elif variable.ndim == 4:
                                var = variable[0, 0, :, :]
                            elif variable.ndim == 5:
                                var = variable[0, 0, 0, :, :]
                            else:
                                var = variable[0, 0, 0, 0, :, :]
                        except (IndexError, ValueError, TypeError) as e:
                            logger.warn(e)
                        else:
                            plt.clf()

                            ax = plt.axes(projection=ccrs.PlateCarree())
                            ax.coastlines()
                            ax.set_global()

                            plt.contourf(lon, lat, var, LEVELS, transform=ccrs.PlateCarree())
                            plt.title(variable.name)
                            plt.subplots_adjust(left=40 / WIDTH, right=1 - 40 / WIDTH, bottom=40 / HEIGHT, top=1 - 40 / HEIGHT)

                            fig = plt.gcf()
                            fig.set_size_inches(WIDTH/DPI, HEIGHT/DPI)
                            fig.savefig(output_abspath, dpi=DPI)

                            return

        except OSError:
            pass

    # if plotting did not work, copy empty.png
    empty_file = Path(__file__).parent.parent / 'extras' / 'empty.png'
    shutil.copyfile(empty_file, output_abspath)
