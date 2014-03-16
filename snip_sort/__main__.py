import argparse
import sys, os
from path import path

from parse import parse_all_inputs, print_output, cull_merged


def main(argv):
    arg_parser = argparse.ArgumentParser(prog="snip_sort",
            description="A program to look up check inclusion for snip data from CLC genomics between several data runs.")
    arg_parser.add_argument('--data_files', '-d', nargs='+',
            required=True, type=path, action='append',
            help="data files to search")
    arg_parser.add_argument('--output_file', '-o',
            required=False, type=path, default="--",
            help="where to save the results. use '--' for stdout")
    arg_parser.add_argument('--minimum', '-m',
            required=False, type=int, default=None,
            help="What the minimum number of hits needed to be included (defaults to 100%)")
    arg_parser.add_argument('--force', '-f',
            required=False,
            action="store_true",
            help="if the output file exists, should we overwrite the file?")
    arg_parser.add_argument('--verbose', '-v', action='store_true',
            required=False,
            default=False, help="print status and completion rate")
    if len(argv) == 1:
        argv.append('--help')
    args = arg_parser.parse_args(argv[1:])
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w',0)
    output_file = args.output_file.abspath()
    if output_file == "--":
        output_fd = sys.stdout
        oddities_fd = sys.stderr
    if output_file.exists():
        if output_file.isdir():
            print "{0} is a directory, please give me a filename".format(output_file)
            sys.exit(1)
        if args.force:
            output_fd = output_file.open("w")
        else:
            print "{0} already exists. use -f to overwrite".format(output_file)
            sys.exit(1)
        oddities_file = path(unicode(output_file.dirname()) + "/" + output_file.namebase + "-oddities" + output_file.ext)
        oddities_fd = oddities_file.open('w')
    else:
        output_fd = output_file.open("w")
        oddities_file = path(unicode(output_file.dirname()) + "/" + output_file.namebase + "-oddities" + output_file.ext)
        oddities_fd = oddities_file.open('w')
    # check that the output folder exists
    input_files = []
    for infi in args.data_files:
        if type(infi) == list:
            infi = [i.abspath() for i in infi]
            input_files += infi
            continue
        if infi.exists():
            input_files += [infi]
            continue
    merged, oddities, all_entries, all_keys = parse_all_inputs(input_files)
    culled, oddities = cull_merged(merged, oddities, all_entries, all_keys, args.minimum)
    print_output(culled, oddities, all_entries, all_keys, output_fd, oddities_fd)
    if args.verbose:
        print "\n\nDONE! :)"

main(sys.argv)
