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
from eofs.iris import Eof
import cartopy.crs as ccrs

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
        # Create an EOF solver to do the EOF analysis. Square-root of cosine of
        # latitude weights are applied before the computation of EOFs.
        solver = Eof(cube, weights='coslat')

        # Retrieve the leading EOF, expressed as the covariance between the leading PC
        # time series and the input SLP anomalies at each grid point.
        eof1 = solver.eofsAsCovariance(neofs=1)

        print(eof1)

        # Plot the leading EOF expressed as covariance in the European/Atlantic domain.
        clevs = np.linspace(-75, 75, 11)
        proj = ccrs.Orthographic(central_longitude=-20, central_latitude=60)
        ax = plt.axes(projection=proj)
        ax.coastlines()
        ax.set_global()
        iplt.contourf(eof1[0, 0], levels=clevs, cmap=plt.cm.RdBu_r)
        ax.set_title('EOF1 expressed as covariance', fontsize=16)
        plt.savefig(os.path.join(cfg["plot_dir"], "eof0.png"))


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
