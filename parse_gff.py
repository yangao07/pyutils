import os, sys
import gffutils as gu
import pysam as ps


def restore_gff_db(gtf_fn):
    gtf_db = None
    if gtf_fn is not None:
        gtf_db_fn = gtf_fn + '.gffdb'
        if not os.path.isfile(gtf_db_fn):
            try:
                format_time(sys.stderr, 'restore_gtf_db', 'Creating gff database for {} ...\n'.format(gtf_fn))
                gtf_db = gu.create_db(gtf_fn, gtf_db_fn)
                format_time(sys.stderr, 'restore_gtf_db', 'Creating gff database for {} done!\n'.format(gtf_fn))

            except:
                format_time(sys.stderr, 'restore_gtf_db',
                            'Error in parsing {}\nCheck if annotation file format is correct\n'.format(gtf_fn))
                sys.exit(IOError)
        else:
            try:
                format_time(sys.stderr, 'restore_gtf_db', 'Retrieving gff database for {} ...\n'.format(gtf_fn))
                gtf_db = gu.FeatureDB(gtf_db_fn)
                format_time(sys.stderr, 'restore_gtf_db', 'Retrieving gff database for {} done!\n'.format(gtf_fn))

            except:
                format_time(sys.stderr, 'restore_gtf_db',
                            'Error in parsing {}\nTry to remove this db file and re-run\n'.format(gtf_db_fn))
                sys.exit(IOError)
    return gtf_db


# return:
# dict{exon_block_ID:[(chr, is_reverse, start, end), ()...]}
def get_exon_block_from_gtf(in_gtf, bam_fn=''):
    gtf_db = ut.restore_gff_db(in_gtf)
    exon_block = {}

    if bam_fn:
        with ps.AlignmentFile(bam_fn) as bam:
            for exon in gtf_db.features_of_type('exon', order_by='start'):
                if exon.attributes['transcript_id'][0] not in exon_block:
                    exon_block[exon.attributes['transcript_id'][0]] = [
                        (bam.get_tid(exon.chrom), exon.strand == '-', int(exon.start), int(exon.end))]
                else:
                    exon_block[exon.attributes['transcript_id'][0]].append(
                        (bam.get_tid(exon.chrom), exon.strand == '-', int(exon.start), int(exon.end)))
    else:
        for exon in gtf_db.features_of_type('exon', order_by='start'):
            if exon.attributes['transcript_id'][0] not in exon_block:
                exon_block[exon.attributes['transcript_id'][0]] = [
                    (exon.chrom, exon.strand == '-', int(exon.start), int(exon.end))]
            else:
                exon_block[exon.attributes['transcript_id'][0]].append(
                    (exon.chrom, exon.strand == '-', int(exon.start), int(exon.end)))
    return exon_block


# return:
# list[[block] [block] ... ]
# block:
# [ID, (exon1), (exon2) ... ]
# exon:
# (chr, is_reverse, start, end)
def get_exon_block_from_bed12(in_bed, bam_fn=''):
    # chr1    9991948 9994918 hsa_circ_0000014        1000    -       9991948 9994918 0,0,255 3       82,96,99        0,912,2871
    # chromStart: 0-base
    # exonStarts: 0-base
    header_ele = ['chrom', 'chromStart', 'chromEnd', 'name', 'score', 'strand',
                  'thickStart', 'thickEnd', 'itemRgb', 'blockCount', 'blockSizes', 'exonStarts']
    bed_header = {header_ele[i]: i for i in range(len(header_ele))}
    exon_block = []
    if bam_fn:
        with open(in_bed, 'r') as bed, ps.AlignmentFile(bam_fn) as bam:
            for line in bed:
                if line.startswith('#'): continue
                ele = line.rsplit('\t')
                chrom = ele[bed_header['chrom']]
                strand = ele[bed_header['strand']]
                start = int(ele[bed_header['chromStart']])
                exon_start = [int(i) for i in ele[bed_header['exonStarts']].split(',')]
                exon_len = [int(i) for i in ele[bed_header['blockSizes']].split(',')]
                exon_block.append([ele[bed_header['name']]])
                for s, l in zip(exon_start, exon_len):
                    exon_block[-1].append((bam.get_tid(chrom), strand == '-', int(start + s + 1), int(start + s + l)))

        exon_block = sorted(exon_block, key=lambda x: (x[1][0], x[1][2], x[-1][3]))
    else:
        with open(in_bed, 'r') as bed:
            for line in bed:
                if line.startswith('#'): continue
                ele = line.rsplit('\t')
                chrom = ele[bed_header['chrom']]
                strand = ele[bed_header['strand']]
                start = int(ele[bed_header['chromStart']])
                exon_start = [int(i) for i in ele[bed_header['exonStarts']].split(',')]
                exon_len = [int(i) for i in ele[bed_header['blockSizes']].split(',')]
                exon_block.append([ele[bed_header['name']]])
                for s, l in zip(exon_start, exon_len):
                    exon_block[-1].append((chrom, strand == '-', int(start + s + 1), int(start + s + l)))
    return exon_block


def gff2len(in_gff, out_fn):
    print in_gff, out_fn
    with open(out_fn, 'w') as out:
        gtf = True if os.path.splitext(in_gff)[1] == '.gtf' else False
        if gtf:
            exon_block = get_exon_block_from_gtf(in_gff)

            for id, b in exon_block.iteritems():
                len = 0
                for exon in b:
                    len += exon[3] - exon[2] + 1
                out.write(id + '\t' + str(len) + '\n')

        else:
            exon_block = get_exon_block_from_bed12(in_gff)
            for b in exon_block:
                id = b[0]
                len = 0
                for exon in b[1:]:
                    len += exon[3] - exon[2] + 1
                out.write(id + '\t' + str(len) + '\n')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage:')
        sys.stderr.write('{} in.gff out.len'.format(sys.argv[0]))
        sys.exit(1)
    gff2len(sys.argv[1], sys.argv[2])
