#!/usr/bin/env python

import sys

# Import matplot lib but avoid default X environment
#  this makes our plots more portable, particularly
#  across Linux systems
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def parse_dragen_gc_content_data(fn):
    """
    Parse data of the form:
        READ GC CONTENT,Read1,45% GC Reads,360933337076
        READ GC CONTENT,Read1,46% GC Reads,342295545717
        READ GC CONTENT,Read1,47% GC Reads,327337356911
        READ GC CONTENT,Read1,48% GC Reads,312960443209
        READ GC CONTENT,Read1,49% GC Reads,297137446765
        READ GC CONTENT,Read1,50% GC Reads,279015902877
    into a dictionary
    """
    data = dict()

    # Parse the raw values into a dictionary by quantile
    with open(fn) as handle:
        for line in handle:
            parts = line.strip().split(',')
            # Skip non-gc-content and non-Read1 data to make this easy
            if parts[0] != "READ GC CONTENT":
                continue
            if parts[1] != "Read1":
                continue
            value = int(parts[3])
            metric = parts[2]
            gc_quantile = int(metric.split('%')[0])

            data[gc_quantile] = value

    # Finde the total value of all of the values found
    total = sum([c for c in data.values()])

    # Normalize the data so it sums to ~= 100%
    data_norm = dict()
    for gc, count in data.items():
        data_norm[gc] = (count / total) * 100
    
    # Return the normalized value
    return data_norm

def gc_content_plot(data, prefix):
    """
    Create a box-and-whisker plot in the style of FastQC, and write
     it out to a PNG file with a given prefix
    """
    # Create the plot object
    fig1, ax1 = plt.subplots(figsize=(16, 4))

    # Set the plot and axis titles
    ax1.set_title('Read GC Content Distribution')
    ax1.set_xlabel('Percent GC Content')
    ax1.set_ylabel('Fraction of Reads')

    # Rotate the x-axis labels 90 degrees since we have so many
    plt.xticks(rotation=90)

    # Extract our key-value pairs into the ordered array that
    #  matplotlib expects
    x = list()
    y = list()
    for key in sorted(data.keys()):
        x.append(key)
        y.append(data[key])

    # Plot the data
    plt.plot(x, y)

    # Tweak the plot boundaries so we have a little more head room,
    #  but don't waste so much space on the sides or bottom
    ax1.set_xlim([0, 100])
    ax1.set_ylim([0, 4.5])

    # Make sure we display a reasonable number of y-axis ticks
    #  neither too many nor too few
    plt.locator_params(axis='y', nbins=5)

    # Add grid-lines to the y-axis now that the ticks are reasonable
    plt.grid(b=True, which='major', axis='y')
    
    # Save the figure to a file with the specified prefix
    filename = "{}.png".format(prefix)
    plt.savefig(filename, bbox_inches='tight')


# This only triggers if the file is executed as a script
if __name__ == "__main__":
    input_filename = sys.argv[1]
    output_prefix = sys.argv[2]

    data = parse_dragen_gc_content_data(input_filename)
    gc_content_plot(data, output_prefix)

