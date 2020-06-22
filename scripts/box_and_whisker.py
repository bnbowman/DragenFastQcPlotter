#! /usr/bin/env python

import sys

from collections import OrderedDict

# Import matplot lib but avoid default X environment
#  this makes our plots more portable, particularly
#  across Linux systems
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def parse_dragen_boxplot_data(fn):
    """
    Parse data of the form:
        POSITIONAL QUALITY,Read1,ReadPos 50 10% Quantile QV,33
        POSITIONAL QUALITY,Read1,ReadPos 50 25% Quantile QV,38
        POSITIONAL QUALITY,Read1,ReadPos 50 50% Quantile QV,40
        POSITIONAL QUALITY,Read1,ReadPos 50 75% Quantile QV,41
        POSITIONAL QUALITY,Read1,ReadPos 50 90% Quantile QV,41
    into a 2D dictionary - first by ReadPos and then by Quantile
    """
    data = OrderedDict()
    with open(fn) as handle:
        for line in handle:
            parts = line.strip().split(',')
            # Skip non-boxplot and non-Read1 data to make this easy
            if parts[0] != "POSITIONAL QUALITY":
                continue
            if parts[1] != "Read1":
                continue
            value = int(parts[3])
            metric = parts[2]
            metric_parts = metric.split()

            pos = metric_parts[1]
            quantile = int(metric_parts[2][:-1])

            try:
                data[pos][quantile] = value
            except:
                data[pos] = {quantile:value}

    return data

def mock_data(data):
    """
    Mock up a fake dataset for a single variable to have given values
     for it's 10, 25, 50, 75, and 90th percentiles
    """
    res = []
    res += [data[10]] * 10
    res += [data[25]] * 25
    res += [data[50]] * 30
    res += [data[75]] * 25
    res += [data[90]] * 10
    return res

def mock_dataset(data):
    """
    Annoyingly, Matplotlib doesn't really let us create box-plots from
     precomputed quantiles, like we get from DRAGEN.  So as a quick
     and dirty hack, we create a mock dataset of 100 elements with
     the desired quantiles for each category (i.e. positon)
    """
    res = []
    for key in data.keys():
        res.append( mock_data(data[key]) )
    return res

def box_and_whisker_plot(data, prefix):
    """
    Create a box-and-whisker plot in the style of FastQC, and write
     it out to a PNG file with a given prefix
    """
    # Create the plot object
    fig1, ax1 = plt.subplots(figsize=(16, 4))

    # Set the plot and axis titles
    ax1.set_title('Quality Scores by Read Position')
    ax1.set_xlabel('Position in Read (bp)')
    ax1.set_ylabel('Base Quality Value')
    
    # Rotate the x-axis labels 90 degrees since we have so many
    plt.xticks(rotation=90)

    # Mock up a dataset by
    mock_ds = mock_dataset(data)

    # mock_ds - our mocked-up datasets, one per position
    # whis - controls our whiskers are displayed.  "range" means they
    #   will always be displayed 
    # patch_artist - required for us to change some plot colors later
    box = ax1.boxplot(mock_ds, whis="range", patch_artist=True)
    
    # Modify our plots to fill our inter-quartile boxes with roughly the
    #  same color as FastQC
    for patch in box['boxes']:
        patch.set_facecolor("yellow")

    # Extend the top of the graph slightly so we can see the tops
    #  of the boxes more clearly
    ax1.set_ylim([0, 43])

    # Fill the background with 3 color rectangles representing broad quality
    #  categories, such that our plots mirror those created by FastQC
    xlim = ax1.get_xlim()
    ax1.barh(0,  xlim[1], height=20,  left=xlim[0], color='#e6c3c3', linewidth=0, zorder=0, align='edge')
    ax1.barh(20, xlim[1], height=28,  left=xlim[0], color='#e6dcc3', linewidth=0, zorder=0, align='edge')
    ax1.barh(28, xlim[1], height=100, left=xlim[0], color='#c3e6c3', linewidth=0, zorder=0, align='edge')

    # Redraw the canvas to apply our color changes
    ax1.figure.canvas.draw()

    # Save the figure to a file with the specified prefix
    filename = "{}.png".format(prefix)
    plt.savefig(filename, bbox_inches='tight')


# This only triggers if the file is executed as a script
if __name__ == "__main__":
    input_filename = sys.argv[1]
    output_prefix = sys.argv[2]

    data = parse_dragen_boxplot_data(input_filename)
    box_and_whisker_plot(data, output_prefix)
