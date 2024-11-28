"""Python example diagnostic."""
import os
import logging
from pathlib import Path
from pprint import pformat
import iris.analysis
import iris.analysis.stats
import matplotlib.pyplot as plt
import iris.quickplot as qplt
import iris.plot as iplt
import numpy as np
import matplotlib.ticker as ticker
import iris

from esmvaltool.diag_scripts.shared import (
    group_metadata,
    run_diagnostic,
)

from esmvaltool.diag_scripts.shared.io import get_ancestor_file


logger = logging.getLogger(Path(__file__).stem)


def main(cfg):
    """Compute the time average for each input dataset."""
    # Get a description of the preprocessed data that we will use as input.
    input_data = cfg['input_data'].values()

    grouped_input_data = group_metadata(input_data,
                                        'variable_group')
    logger.info(
        "Example of how to group and sort input data by variable groups from "
        "the recipe:\n%s", pformat(grouped_input_data))
    eof_file = get_ancestor_file(cfg, pattern="*eof*.nc")
    eof = iris.load_cube(eof_file)
    for group_name in grouped_input_data:
        logger.info("Processing variable %s", group_name)
        cube = iris.load_cube(grouped_input_data[group_name][0]["filename"])
        corr = iris.analysis.stats.pearsonr(cube, eof[0], corr_coords=["time"])
        plt.figure()
        mx=np.max(np.abs(corr.data))
        qplt.pcolormesh(regrid_longitude_coord(corr), vmin=-mx, vmax=mx, cmap=plt.cm.RdBu_r)
        plt.savefig(os.path.join(cfg["plot_dir"], f"{group_name}_correlation_map.png"))

def regrid_longitude_coord(cube):
    """Sorts the longitudes of the cubes from 0/360 degrees to -180/180"""
    coord = cube.coord("longitude")
    lon_extent = iris.coords.CoordExtent(coord, -180., 180., True, False)
    cube = cube.intersection(lon_extent)
    return cube

if __name__ == '__main__':
    with run_diagnostic() as config:
        main(config)
