# DRAGEN-FastQc Plotting Utilities

## USAGE

Usage is:
```
python  <script_file.py>  dragen.fastqc_metrics.csv  <output_file_prefix>
```

For example, to re-generate the gc-content plot as it appears in this repo:
```
python  scripts/gc_content.py  data/dragen.fastqc_metrics.csv  gc_content
```

NOTE:  Settings for size/resolution/etc. are mostly defaults copied from MultiQC, and aren’t final.  They probably need to be changed, and definitely need to be made somewhat configurable.

The general idea is to have one of these little scripts per plot we want, along with a wrapper like “dragen_plotter.py” or whatever that calls all of them.
