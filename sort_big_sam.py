import argparse
import pysam as ps
import sys
import re
import os
from collections import defaultdict as dd
__program__ = 'sort_big_bam'
__version__ = '1.0.0'


def parser_argv():
    # parse command line arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="{}: sort big SAM file using low memory".format(__program__))
    parser.add_argument('in_sam', metavar='in.unsorted.sam', type=str, help='Input SAM file')

    general_par = parser.add_argument_group('general options')
    general_par.add_argument('-o', '--output', type=str, default='', help='output folder, use folder of input SAM file by default')
    general_par.add_argument('-s', '--split', type=bool, default=False, help='keep chromosome-wise splited BAM file')
    general_par.add_argument('-v', '--version', action='version', version=__program__ + ' ' + __version__)

    return parser.parse_args()


def sort_big_bam(in_sam, out_pre, keep_split):
    in_sam_fp = ps.AlignmentFile(in_sam)
    out_bam = out_pre + '.sorted.bam'
    header = in_sam_fp.header
    out_sam_dict = dd(lambda: dd(lambda: None))
    for ref in header.references:
        out_unsorted_bam_fn = out_pre + '.' + ref + '.unsorted.bam'
        out_sorted_bam_fn = out_pre + '.' + ref + '.sorted.bam'
        out_unsorted_bam_fp = ps.AlignmentFile(out_unsorted_bam_fn, 'wb', template=in_sam_fp)
        out_sam_dict[ref]['unsorted_fp'] = out_unsorted_bam_fp
        out_sam_dict[ref]['unsorted_fn'] = out_unsorted_bam_fn
        out_sam_dict[ref]['sorted_fn'] = out_sorted_bam_fn

    for r in in_sam_fp:
        ref_name = r.reference_name
        if ref_name not in out_sam_dict:
            sys.stderr.write('Unexpected reference name: {} ({})'.format(ref_name, r.query_name))
            sys.exit(1)
        out_unsorted_bam_fp = out_sam_dict[ref_name]['unsorted_fp']
        out_unsorted_bam_fp.write(r)
    for ref in out_sam_dict:
        out_sam_dict[ref]['unsorted_fp'].close()
        out_unsorted_bam_fn = out_sam_dict[ref]['unsorted_fn']
        out_sorted_bam_fn = out_sam_dict[ref]['sorted_fn']
        ps.sort(out_unsorted_bam_fn, "-o", out_sorted_bam_fn)
        os.system('rm {}*'.format(out_unsorted_bam_fn))

    with ps.AlignmentFile(out_bam, 'wb', template=in_sam_fp) as out_bam_fp:
        for ref in header.references:
            sorted_sam_fn1 = out_sam_dict[ref]['sorted_fn']
            with ps.AlignmentFile(sorted_sam_fn1) as sam_fp1:
                for r in sam_fp1:
                    out_bam_fp.write(r)
            if not keep_split:
                os.system('rm {}*'.format(sorted_sam_fn1))
    in_sam_fp.close()


def sort_big_bam_main(args):
    in_sam = args.in_sam
    basename = os.path.basename(in_sam)
    if args.output == '':
        out_dir = os.path.dirname(os.path.abspath(in_sam))
    else:
        out_dir = os.path.dirname(os.path.abspath(args.output))
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    keep_split = args.split
    out_pre = out_dir + '/' + re.sub(r'.sam$', '.sorted.bam', basename)
    sort_big_bam(in_sam, out_pre, keep_split)


if __name__ == '__main__':
    args = parser_argv()
    sys.stderr.write('{}'.format(' '.join(sys.argv)))
    sort_big_bam_main(args)
