"""Python example diagnostic."""
import os
import logging
from pathlib import Path
from pprint import pformat
import matplotlib.pyplot as plt
import iris.quickplot as qplt
import iris.plot as iplt
import numpy as np

import iris

from esmvaltool.diag_scripts.shared import (
    group_metadata,
    run_diagnostic,
)

logger = logging.getLogger(Path(__file__).stem)


def plot_diagnostic(groups, cfg):
    """Create diagnostic data and plot it."""
    plt.figure()
    for attributes in groups:
        logger.info("Processing dataset %s", attributes['dataset'])
        input_file = attributes['filename']
        cube = iris.load_cube(input_file)
        dims = len(cube.shape)
        if dims == 2 and attributes['dataset'] == "MultiModelMean":
            qplt.pcolormesh(cube, cmap=cfg["cmap"])
            plt.gca().coastlines()
        elif dims == 1:
            dim_name = [i.long_name for i in cube.coords()]
            if "month_number" in dim_name:
                time_coord = np.arange(1,13)
            else:
                time_coord = [i.year for i in cube.coord("time").units.num2date(cube.coord("time").points)]
            if attributes['dataset'] == "MultiModelMean":
                plt.plot(time_coord, cube.data, color="black")
            else:
                plt.plot(time_coord, cube.data, alpha=0.5)

    title = cube.long_name
    plt.ylabel(f"{cube.standard_name} / degC")
    plt.title(attributes['caption'].format(title=title.lower()))
    plt.tight_layout()
    plt.savefig(os.path.join(cfg["plot_dir"], attributes["savefig"]), bbox_inches="tight")

def main(cfg):
    """Compute the time average for each input dataset."""
    # Get a description of the preprocessed data that we will use as input.
    input_data = cfg['input_data'].values()

    grouped_input_data = group_metadata(input_data,
                                        'variable_group')
    logger.info(
        "Example of how to group and sort input data by variable groups from "
        "the recipe:\n%s", pformat(grouped_input_data))
    for group_name in grouped_input_data:
        logger.info("Processing variable %s", group_name)
        plot_diagnostic(grouped_input_data[group_name], cfg)


if __name__ == '__main__':
    with run_diagnostic() as config:
        main(config)
