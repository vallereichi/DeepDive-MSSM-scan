
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from util import load_hdf5_file, Scan, Observable
from scan_info import scan_info

"""
define defaults for testing 
"""
path_to_runs = "../runs/version1"
path_to_diver_scan = "../runs/version1/MSSM_diver/samples/DIVER.hdf5"
path_to_random_scan = "../runs/version1/MSSM_random/samples/RANDOM.hdf5"

COLORS = ['coral', 'darkcyan', 'orchid', 'darkseagreen', 'goldenrod']

observable_list = [
    "h0_1",
    "A0",
#    "chi0_1",
#    "chi0_2",
#    "chi0_3",
#    "~chi+",
#    "~chi-",
#    ":t",
#    "mstop1",
#    "mstop2",
#    "sinW2 dimensionless",
#    "tanbeta",
#    "Z0",
#    ":W+",

    ]






"""
function declarations
"""
def search_observable(scan:Scan, search:str) -> str:
    """
    Find a search string in a pandas dataframe and return the key of the column.

    parameters:
        scan: pandas dataframe
        search: string to search for

    returns:
        key of the column as string
    """
    key = ''
    for string in scan.keys():
        if re.search(f'{search}(?!.*_isvalid)', string) is not None:
            key = string
            print("Key found: ", key)
            break

    if key == '':
        raise ValueError(f"no key found for '{search}'")
    
    return key


def get_dimension(observable_key:str) -> str:
    """
    determine the unit of the observable

    parameters:
        observable_key: key of the observable

    returns:
        string with the unit of the observable
    """
    dim = ''
    if re.search('Pole_Mass', observable_key) is not None:
        dim = "mass [GeV]"

    return dim



# create plots
def scatter_2d(scan_list:list[Scan], observable_list:list[Observable]) -> None:
    """
    create a 2D scatter plot of two observables

    parameters:
        scan_list: list of Scan objects
        observable_list: list of observables to plot. length must be even
        
    returns:
        None
    """
    
    # start 2D scatter plot
    for scan in scan_list:
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111)
        ax.scatter(scan[observable_list[0].key], scan[observable_list[1].key], c=scan['plr'], cmap='viridis', s=10)
        ax.set_xlabel(f"{observable_list[0].label} {observable_list[0].unit}")
        ax.set_ylabel(f"{observable_list[1].label} {observable_list[1].unit}")
        ax.set_title(scan.name)

        fig.tight_layout()
        #plt.show()
        fig.savefig(f"../plots/2D_scatter_plot_{observable_list[0].label}_{observable_list[1].label}_{scan.name}.png", dpi=1000)
        plt.close(fig)

        # TODO: add better colomap
        
        # TODO: add capability to handle more than two observables

    return


def plot_plr(scan_list:list[Scan], observable_list:list[Observable]) -> None:
    """
    create a 2D scatter plot of two observables

    parameters:
        scan_list: list of Scan objects
        observable_list: list of observables to plot. length must be even
        
    returns:
        None
    """

    # start profile likelihood ratio plot
    for obs in observable_list:
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111)
        labels = []
        for id, scan in enumerate(scan_list):
            ax.scatter(scan[obs.key], scan['plr'], c=COLORS[id], alpha=0.5)
            labels.append(scan.name + ": $\\mathcal{L}_{max} = $" + str(scan[obs.key][scan['plr'].idxmax()].round(2)))
        ax.set_xlabel(f"{obs.label} {obs.unit}")
        ax.set_ylabel("Profile Likelihood Ratio $\\mathcal{L}$")
        ax.legend(labels)
        

        fig.tight_layout()
        #plt.show()
        fig.savefig(f"../plots/plr_plot_{obs.label}.png", dpi=1000)
        plt.close(fig)

        
    return
    


def hist_1d(scan_list:list[Scan], observable_list:list[Observable]) -> None:
    """
    create a 1D histogram plot of an observable. Provide more than one scan to compare them.

    parameters:
        scan_list: list of Scan objects
        observable_list: list of observables to plot

    returns:
        None
    """

    for obs in observable_list:
        # calculate bins
        n_bins = 20
        bin_range = abs(scan_list[0][obs.key].max() - scan_list[0][obs.key].min())
        step_size = bin_range / n_bins
        try:
            bins = np.arange(scan_list[0][obs.key].min(), scan_list[0][obs.key].max(), step_size)
        except : 
            print(f"Could not calculate bins for {obs.label}. Check the data.")
            continue

        # start 1D histogram plot
        labels = []
        counts = [] 
        fig = plt.figure(figsize=(6, 6))
        if len(scan_list) == 2:
            gs = fig.add_gridspec(2, 1, height_ratios=(3,1), hspace=0)
            ax = fig.add_subplot(gs[0])
        else:
            ax = fig.add_subplot(111)
        for id_scan, scan in enumerate(scan_list):
            count, _, _ = ax.hist(scan[obs.key], bins=bins, density=True, alpha=0.5, color=COLORS[id_scan+1])
            counts.append(count)
            labels.append(scan.name + ": $\\mathcal{L}_{max} = $" + str(scan[obs.key][scan['plr'].idxmax()].round(2)))
        ax.set_ylabel("Counts")
        ax.legend(labels)
        ax.set_xticks([])

        # calculate count ratio
        if len(scan_list) == 2:
            ax_ratio = fig.add_subplot(gs[1])
            ratio = counts[1] / counts[0]
            xaxis = [bins[i]+0.5*step_size for i in range(len(bins)-1)]
            ax_ratio.scatter(xaxis, ratio, color='black', alpha=0.5, marker='.')
            ax_ratio.set_xlabel(f"{obs.label} {obs.unit}")
            ax_ratio.set_ylabel("Ratio")
            ax_ratio.legend([scan_list[1].name + " / " + scan_list[0].name])
            ax_ratio.grid(linestyle='--', color='grey', alpha=0.5)
            ax_ratio.set_ylim(-0.5, ax_ratio.get_ylim()[1] + 0.5)



        fig.tight_layout()
        #plt.show()
        fig.savefig(f"../plots/hist_plot_{obs.label}.png", dpi=1000)
        plt.close(fig)
    return



# Entry point
if __name__ == "__main__":

    scan_list = load_hdf5_file(path_to_runs)
    keys = [search_observable(scan_list[0], observable) for observable in observable_list]
    dimensions = [get_dimension(key) for key in keys]
    observable_list = [Observable(observable, key, dim) for observable, key, dim in zip(observable_list, keys, dimensions)]
    
    for obs in observable_list:
        print(obs)
    if len(observable_list) == 2:
        scatter_2d(scan_list, observable_list)
    plot_plr(scan_list, observable_list)
    hist_1d(scan_list, observable_list)