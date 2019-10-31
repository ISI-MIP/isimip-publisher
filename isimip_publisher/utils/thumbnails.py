import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from netCDF4 import Dataset

WIDTH = 800
HEIGHT = 380
DPI = 96


def write_dataset_thumbnail(dataset_abspath, files):
    write_file_thumbnail(files[-1], output_abspath='%s.png' % dataset_abspath)


def write_file_thumbnail(file_abspath, output_abspath=None):
    if not output_abspath:
        output_abspath = file_abspath.replace('.nc4', '.png')

    with Dataset(file_abspath, mode='r') as dataset:
        var_name = list(dataset.variables)[0]

        lat = dataset.variables['lat'][:]
        lon = dataset.variables['lon'][:]
        var = dataset.variables[var_name][-1, :, :]

        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()

        plt.contourf(lon, lat, var, 10, transform=ccrs.PlateCarree())
        plt.title(var_name)

        fig = plt.gcf()
        fig.tight_layout()
        fig.set_size_inches(WIDTH/DPI, HEIGHT/DPI)
        fig.savefig(output_abspath, dpi=DPI)

        # reset plt
        plt.clf()
