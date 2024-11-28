"""Python example diagnostic."""
import os
import logging
from pathlib import Path
from pprint import pformat
import matplotlib.pyplot as plt
import iris.quickplot as qplt
import iris.plot as iplt
import numpy as np
import matplotlib.ticker as ticker
import iris
import cartopy.crs as ccrs
from scipy.linalg import svd
import xeofs
import xarray as xr

from esmvaltool.diag_scripts.shared import (
    group_metadata,
    run_diagnostic,
)

logger = logging.getLogger(Path(__file__).stem)


def eof_compute(groups, cfg):
    """Create diagnostic data and plot it."""
    plt.figure()
    for attributes in groups:
        logger.info("Processing dataset %s", attributes['dataset'])
        input_file = attributes['filename']
        cube = iris.load_cube(input_file)

        model = xeofs.models.EOF(n_modes=100, standardize=True, use_coslat=True)
        model.fit(xr.DataArray.from_iris(cube), dim="time")
        components_eof = model.components()
        scores_eof = model.scores()
        rot_var = xeofs.models.EOFRotator(n_modes=50, power=1)
        rot_var.fit(model)
        components_roteof = rot_var.components().to_iris() # EOF
        scores_roteof = rot_var.scores().to_iris() # PCA
        expvar_ratio = rot_var.explained_variance_ratio()

        eof1 = components_roteof[0]
        var1 = expvar_ratio[0]
        pc1 = scores_roteof[0]

        print(eof1)
        print(pc1)

        iris.save(components_roteof, os.path.join(cfg["work_dir"], "natl_eof.nc"))
        iris.save(scores_roteof, os.path.join(cfg["work_dir"], "natl_pca.nc"))

        mx = np.max(np.abs(eof1.data))
        # Plot the leading EOF expressed as covariance in the European/Atlantic domain.
        clevs = np.linspace(-mx, mx, 11)
        # Create a figure with 2 panels: one for the map and one for the PC time series
        fig = plt.figure(figsize=(10, 8))

        # Create the map plot (top panel)
        ax_map = fig.add_subplot(2, 1, 1, projection=ccrs.PlateCarree())
        ax_map.set_title(f'North Atlantic Oscillation (NAO) - EOF Map- Var. {var1:.02}%')
        ax_map.coastlines()
        # ax_map.add_feature(cfeature.BORDERS, linestyle=':')
        # ax_map.set_extent([-80, 30, 30, 70], crs=ccrs.PlateCarree())
        iplt.contourf(regrid_longitude_coord(eof1), levels=clevs, cmap=plt.cm.RdBu_r)

        ax_pc = fig.add_subplot(2, 1, 2)
        ax_pc.set_title('Principal Component (PC) Score')
        iplt.plot(pc1, color='blue', label='PC1')
        ax_pc.axhline(0, color='black', linewidth=0.8, linestyle='--')  # Add a zero line
        ax_pc.set_xlabel('Time Index')
        ax_pc.set_ylabel('PC Amplitude')
        ax_pc.legend()

        plt.savefig(os.path.join(cfg["plot_dir"], "eof1.png"))

def regrid_longitude_coord(cube):
    """Sorts the longitudes of the cubes from 0/360 degrees to -180/180"""
    coord = cube.coord("longitude")
    lon_extent = iris.coords.CoordExtent(coord, -180., 180., True, False)
    cube = cube.intersection(lon_extent)
    return cube

def main(cfg):
    """Compute the time average for each input dataset."""
    # Get a description of the preprocessed data that we will use as input.
    input_data = cfg['input_data'].values()

    alias_input_data = group_metadata(input_data,
                                        'alias')
    logger.info(
        "Example of how to group and sort input data by variable groups from "
        "the recipe:\n%s", pformat(alias_input_data))
    for alias in alias_input_data:
        logger.info("Processing variable %s", alias)
        eof_compute(alias_input_data[alias], cfg)


if __name__ == '__main__':
    with run_diagnostic() as config:
        main(config)
