import pysam as ps
import sys
import os
from collections import defaultdict as dd


cov_plot_R_scr = '/home/gaoy1/program/pyutils/cov_plot.R'


def get_win_index(qname, map_pos, chrome_size, win_size):
    if map_pos > chrome_size or map_pos < 1:
        sys.stderr.write('Unexpected mapping position: {} ({})\n'.format(map_pos, qname))
    return int(map_pos / win_size)


def bam_to_cov(in_bam_fn, win_size):
    cov_dict = dd(lambda: dd(lambda: 0))  # chr: window: count
    chr_len = dict()
    with ps.AlignmentFile(in_bam_fn) as in_bam:
        bam_header = in_bam.header
        for chrom in bam_header.references:
            chr_len[chrom] = bam_header.get_reference_length(chrom)
        for r in in_bam:
            if r.is_unmapped or r.is_supplementary or r.is_secondary:
                continue
            qname, chrom, qpos = r.query_name, r.reference_name, r.reference_start+1  # reference_start is 0-based
            win_idx = get_win_index(qname, qpos, chr_len[chrom], win_size)
            cov_dict[chrom][win_idx] += 1
    return cov_dict, chr_len


def plot_cov(cov_dict, chr_len, win_size, plot_fn):
    # generate coverage data
    cov_data = plot_fn + '.dat'
    with open(cov_data, 'w') as out_fp:
        out_fp.write('chrom\twindow\tcov\n')
        for chrom, chr_len in chr_len.items():
            if len(chrom) > 5:
                continue
            win_tot_cnt = int(chr_len / win_size)
            for idx in range(win_tot_cnt+1):
                out_fp.write('{}\t{}\t{}\n'.format(chrom, idx * win_size, cov_dict[chrom][idx]))

    cmd = 'Rscript {} {} {}'.format(cov_plot_R_scr, cov_data, plot_fn)
    sys.stdout.write(cmd)
    # os.system(cmd)


# win_size = 100,000 ?
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('{} in.bam window_size out_coverage.pdf'.format(sys.argv[0]))
        print('\t\twindow size: recommended 100,000')
        sys.exit(1)
    in_bam_fn, win_size, out_pdf = sys.argv[1:]
    win_size = int(win_size)
    cov_per_chr, chr_len = bam_to_cov(in_bam_fn, win_size)
    plot_cov(cov_per_chr, chr_len, win_size, out_pdf)
