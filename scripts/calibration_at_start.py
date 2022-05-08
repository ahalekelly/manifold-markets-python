"""Calibration across all resolved markets
Currently only works for binary markets.
"""
import numpy as np
from matplotlib import pyplot as plt
from manifold import api, calibration


def plot_calibration(c_table, bins):
    _, ax = plt.subplots()
    if bins is None:
        bins = np.arange(0, 1.01, 0.01)
    ax.scatter(bins, c_table)
    # Perfect calibration line
    l = np.arange(0, bins.max(), 0.0001)
    ax.scatter(l, l, color='red', s=0.01)

    plt.show()


def main():
    markets = api.get_full_markets_cached()
    import pdb
    pdb.set_trace()



if __name__ == "__main__":
    main()
