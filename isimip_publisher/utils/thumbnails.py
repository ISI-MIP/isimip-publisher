import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from netCDF4 import Dataset

WIDTH = 800
HEIGHT = 380
DPI = 96
LEVELS = 10


def write_dataset_thumbnail(dataset_abspath, files):
    write_file_thumbnail(files[-1], output_abspath='%s.png' % dataset_abspath)


def write_file_thumbnail(file_abspath, output_abspath=None):
    if not output_abspath:
        output_abspath = file_abspath.replace('.nc4', '.png')

    with Dataset(file_abspath, mode='r') as dataset:

        for var_name, variable in dataset.variables.items():
            if len(variable.dimensions) > 1:
                break

        plt.axes(projection=ccrs.PlateCarree()).coastlines()
        plt.title(var_name)

        try:
            lat = dataset.variables['lat'][:]
            lon = dataset.variables['lon'][:]
            var = dataset.variables[var_name][-1, :, :]

            plt.contourf(lon, lat, var, LEVELS, transform=ccrs.PlateCarree())
        except (IndexError, ValueError):
            pass

        fig = plt.gcf()
        fig.set_size_inches(WIDTH/DPI, HEIGHT/DPI)
        fig.savefig(output_abspath, dpi=DPI)

        # reset plt
        plt.clf()
