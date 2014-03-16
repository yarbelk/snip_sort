snip_sort
=========

Script for sorting snips from dna based on Chromosome and pos, with filtering for minimum number of inclusions across all data sets. 


Installing
----------

assuming you have pip installed (as root run)

    pip install git+https://github.com/yarbelk/snip_sort.git

Running:
--------

to run snip_sort, just type snip_sort (installing above installs the script as a command line program)

    snip_sort -d path/to/*.vcf -o path/to/outputfile.vcf

the help has more information on the different options.

    snip_sort --help
