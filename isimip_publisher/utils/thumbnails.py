import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from netCDF4 import Dataset

WIDTH = 800
HEIGHT = 800
DPI = 96


def write_dataset_thumbnail(file_path):
    print(file_path)


def write_file_thumbnail(file_path):
    output_file_path = file_path.replace('.nc4', '.png')

    with Dataset(file_path, mode='r') as dataset:
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
        fig.savefig(output_file_path, dpi=DPI)

        # reset plt
        plt.clf()
