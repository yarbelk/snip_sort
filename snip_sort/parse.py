from path import path
from collections import Counter
import sys

FILE_HEADER="""##fileformat=VCFv4.1
##fileDate=20140304
##fileEncoding=UTF-8
##source=CLC Genomics Workbench 7.0 build 700105893
##reference=file:/home/yweechieh/CLC_Data/P%20nodosus%20RAD%20test2/Q-based%20Variant%20detection/Chek%20Jawa/QV04F1-CJ03T2-RM6-T2A5A11.clc
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total number of filtered reads per sample used by variant caller">
##FORMAT=<ID=CLCAD2,Number=.,Type=Integer,Description="Allelic depth, number of filtered reads supporting the alleles where the first element represents the reference and subsequent elements represent the alternatives in the order listed in the ALT column">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	"""

def get_lines_of_data(filename, all_entries):
    this_file = {}
    header = None
    key_set = []
    with open(filename, 'r') as fd:
        for line in fd:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0:2] == '##':
                continue
            if line[0] == '#':
                header = line.split('\t')
                key_set = header[9:]
                for i, key in enumerate(key_set):
                    key_set[i] = key.split('-')[1]
                continue
            full_data = line.split('\t')
            data = full_data[9:]

            full_data[0] = full_data[0] + "--" + full_data[1]
            line_key = tuple(full_data[:9])
            all_entries.append(line_key)

            if line_key in this_file:
                print "Something went wrong - duplicate line: {}".format(line_key)
            else:
                this_file[line_key] = {}

            for i, key in enumerate(key_set):
                this_file[line_key][key] = data[i]
    return key_set, this_file


def parse_all_inputs(filelist):
    """
    merged format:
    {(chrom, pos):{(ref,alt): {full_data:{key:datum} } } }
    """
    all_entries = []
    all_keys = []
    per_filename = {}
    for filename in filelist:
        key_set, file_data = get_lines_of_data(filename, all_entries)
        all_keys += key_set
        per_filename[filename] = file_data

    merged = {}
    oddities = {}
    for filename in per_filename:
        for data in per_filename[filename]:
            # Case where there is a  problem against the reference
            if ',' in data[4] or len(data[3]):
                if data not in oddities:
                    oddities[data] = per_filename[filename][data]
                else:
                    oddities[data].update(per_filename[filename][data])
            natural_key = tuple(data[:2])
            if natural_key not in merged:
                merged[natural_key] = {}
            ref_alt = tuple(data[3:5])
            if ref_alt not in merged[natural_key]:
                merged[natural_key][ref_alt] = {}
            if data not in merged[natural_key][ref_alt]:
                merged[natural_key][ref_alt][data] = per_filename[filename][data]
            else:
                merged[natural_key][ref_alt][data].update(per_filename[filename][data])


    all_entries_set = sorted(set(all_entries))
    all_keys_set = sorted(set(all_keys))
    return (merged, oddities, all_entries_set, all_keys_set)


def get_counts(merged, all_entries_set, all_keys_set):
    """
    entry is the first 9 elements (natural key)
    """
    C = Counter()
    for entry in all_entries_set:
        for key in all_keys_set:
            if key in merged[entry]:
                C[entry] += 1
    return C


def get_max_subset(snip):
    """for a snip (chrom, region), find the (ref,alt) with the most matches,
    return that for the culled data, and the rest for the oddities"""
    C = Counter()
    for ref_alt in snip:
        for full_datum in snip[ref_alt]:
            C[ref_alt] += len(snip[ref_alt][full_datum])
    max_ref_alt = max(C)
    oddities = {}
    culled = {snip[max_ref_alt].keys()[0]:
                  snip[max_ref_alt][snip[max_ref_alt].keys()[0]]}
    keys = snip.keys()
    keys.remove(max_ref_alt)
    for key in keys:
        oddities[snip[key].keys()[0]] = snip[key][snip[key].keys()[0]]

    return culled, oddities


def cull_merged(merged, oddities, all_entries_set, all_keys_set, minimum=None):
    if minimum == None:
        minimum = len(all_keys_set)
    culled = {}
    C = Counter()
    for natural_key in merged:
        snip = merged[natural_key]
        new_culled, new_oddities = get_max_subset(snip)
        for entry in new_culled:  # len 1
            if len(new_culled[entry]) >= minimum:
                culled.update(new_culled)
        oddities.update(new_oddities)

    return culled, oddities


def print_output(merged, oddities, all_entries_set, all_keys_set, output_fd, oddities_fd):
    header = FILE_HEADER + "\t".join(all_keys_set) + '\n'
    output_fd.write(header)
    oddities_fd.write(header)
    for entry in all_entries_set:
        output_tmp = list(entry)
        oddity_tmp = list(entry)
        for key in all_keys_set:
            if entry in merged:
                output_value = merged[entry].get(key, "./.")
                output_tmp += [output_value]
            if entry in oddities:
                oddity_value = oddities[entry].get(key, "./.")
                oddity_tmp += [oddity_value]
        if entry in merged:
            output_fd.write("\t".join(output_tmp) + "\n")
        if entry in oddities:
            oddities_fd.write("\t".join(oddity_tmp) + "\n")
