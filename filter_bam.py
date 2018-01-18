import os, sys
import pysam as ps
import parse_bam as pb
import utils as ut

def get_high_qual_bam(in_bam, out_bam, cov=0.67, iden_frac=0.75, sec_ratio=0.98):
    infile = ps.AlignmentFile(in_bam)
    outfile = ps.AlignmentFile(out_bam, "wb", template=infile)

    last_name = ''

    b_score, s_score, score, cnt = 0, 0, 0, 0
    best_r = None

    ut.format_time(stderr, 'Filter_BAM', 'Start to filtered alignment records ...')

    for in_r in infile:
        score =  bam_filter(in_r, cov, iden_frac)
        if score < 0: continue
        if in_r.query_name == last_name:
            if score > b_score:
                best_r = in_r
                s_score = b_score
                b_score = score
            elif score > s_score:
                s_score = score
        else:
            if last_name and s_score < sec_ratio * b_score:
                outfile.write(best_r)
                cnt += 1
            best_r = in_r
            b_score, s_score = score, 0
            last_name = in_r.query_name
    if last_name and s_score < sec_ratio * b_score:
        outfile.write(best_r)
        cnt += 1

    ut.format_time(stderr, 'Filter_BAM', 'Filtered alignment records: {}'.format(cnt))
    infile.close()
    outfile.close()