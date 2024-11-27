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

from esmvaltool.diag_scripts.shared import (
    group_metadata,
    run_diagnostic,
    get_ancestor_file
)

logger = logging.getLogger(Path(__file__).stem)


def plot_diagnostic(groups, cfg):
    """Create diagnostic data and plot it."""
    eof_file = get_ancestor_file(cfg, pattern="*eof*.nc")
    eof = iris.load_cube(eof_file)
    for attributes in groups:
        logger.info("Processing dataset %s", attributes['dataset'])
        input_file = attributes['filename']
        cube = iris.load_cube(input_file)
        

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
        # plot_diagnostic(grouped_input_data[group_name], cfg)


if __name__ == '__main__':
    with run_diagnostic() as config:
        main(config)
