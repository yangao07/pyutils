import sys, os
import time
import gffutils as gu


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


def format_time(fp, header, str):
    fp.write('==' + time.strftime("%b %d %Y %H:%M:%S", time.localtime()) + '== [' + header + '] ' + str)


def exec_cmd(fp, header, cmd):
    format_time(fp, header, '[CMD] ' + cmd + '\n')
    os.system(cmd)
