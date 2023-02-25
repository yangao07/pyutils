#!/usr/bin/env python
import os
import argparse
import re
import sys
import time

com_cmd = {'tar.gz': 'tar zcvf',
           'tar.tgz': 'tar zcvf',
           'tar.bz2': 'tar jcvf',
           'tar': 'tar cvf',
           'gz': 'gzip',
           'bz2': 'bzip2 -z',
           'zip': 'zip',
           'rar': 'rar a'}
decom_cmd = [('tar.gz', 'tar zxvf'),
             ('tar.tgz', 'tar zxvf'),
             ('tar.bz2', 'tar jxvf '),
             ('tar.xz', 'tar xf'),
             ('tar', 'tar xvf'),
             ('gz', 'gzip -d'),
             ('bz2', 'bzip2 -d'),
             ('zip', 'unzip'),
             ('rar', 'rar x')]

def format_time(fp, header, str):
    fp.write('==' + time.strftime(" %H:%M:%S-%b-%d-%Y ", time.localtime()) + '== [' + header + '] ' + str + '\n')

def fatal_format_time(header, str):
    err_format_time(header, str)
    sys.exit(1)

def exec_cmd(fp, header, cmd):
    format_time(fp, header, cmd)
    ret = os.system(cmd)
    # sys.stderr.write('ret: {}'.format(ret) + '\n')
    if ret != 0:
        fatal_format_time(header, 'Error: ' + cmd)

def compress(in_folder='', type='tar.gz'):
    if type == 'gz':
        exec_cmd(sys.stderr, 'Compress', '{} {}'.format('gzip', in_folder))
        format_time(sys.stderr, 'Compress',  '\'{}\' done!'.format(in_folder))
    if type in com_cmd:
        exec_cmd(sys.stderr, 'Compress','{} {}.{} {}'.format(com_cmd[type], in_folder, type, in_folder))
        format_time(sys.stderr, 'Compress',  '\'{}\' done!'.format(in_folder))
    else:
        sys.stderr.write("Unknown compressed type: \'{}\'.\n".format(type))

def decompress(in_file=''):
    for de_cmd in decom_cmd:
        if in_file.endswith('.'+de_cmd[0]):
            exec_cmd(sys.stderr, 'Decompress', '{} {}'.format(de_cmd[1], in_file))
            format_time(sys.stderr, 'Decompress',  '\'{}\' done!'.format(in_file))
            return
    sys.stderr.write("Unknown compressed type: \'{}\'.\n".format(in_file))

def parser_argv():
    # parse command line arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="Compress and decompress file toolkit.")
    parser.add_argument("in_file", metavar='file/folder', type=str,
                        help='File to decompress or folder to compress.')
    parser.add_argument("--type", type=str, default='tar.gz',
                        choices=['tar.gz', 'tar.tgz', 'tar.bz2', 'tar', 'gz', 'bz2', 'zip', 'rar'],
                        help='Compressed file type.')
    return parser.parse_args()

if __name__ == '__main__':
    args = parser_argv()
    if os.path.isdir(args.in_file):
        compress(args.in_file, args.type)
    else:
        decompress(args.in_file)
