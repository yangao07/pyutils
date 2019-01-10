#!/usr/bin/env python
import os
import argparse
import re
import sys

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
             ('tar', 'tar xvf'),
             ('gz', 'gzip -d'),
             ('bz2', 'bzip2 -d'),
             ('zip', 'unzip'),
             ('rar', 'rar x')]


def compress(in_folder='', type='tar.gz'):
    if type == 'gz':
        os.system('{} {}'.format('gzip', in_folder))
    if type in com_cmd:
        os.system('{} {}.{} {}'.format(com_cmd[type], in_folder, type, in_folder))
    else:
        sys.stderr.write("Unknown compressed type: {}.\n".format(type))

def decompress(in_file=''):
    for de_cmd in decom_cmd:
        if in_file.endswith('.'+de_cmd[0]):
            os.system('{} {}'.format(de_cmd[1], in_file))
            return
    sys.stderr.write("Unknown compressed type: {}.\n".format(type))

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
