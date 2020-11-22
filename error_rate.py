import os, sys
import pysam as ps
from collections import defaultdict as dd
import mappy as mp
from pyfaidx import Fasta

ep_header = ['#READ_NAME',      'READ_LEN', 'UNMAP',   'INS',     'DEL',     'MIS',     'MATCH',   'CLIP',    'SKIP',    'ERR_RATE']
ep_idx = {j: i for i,j in enumerate(ep_header)}

info_header = ['CONS_NAME', 'READ_LEN', 'CONS_LEN', 'COPY_NUM', 'ID_RATE', 'FLAG']
info_idx = {j: i for i,j in enumerate(info_header)}

ref_fa='/home/gaoy1/data/genome/hg19.fa'
read_fas=[
'/home/gaoy1/circRNA/raw_long_reads/nano_43.fa',
'/home/gaoy1/circRNA/raw_long_reads/nano_44.fa',
'/home/gaoy1/circRNA/raw_long_reads/nano_45.fa',
'/home/gaoy1/circRNA/raw_long_reads/nano_58.fa',
'/home/gaoy1/circRNA/raw_long_reads/nano_59.fa',
'/home/gaoy1/circRNA/raw_long_reads/nano_60.fa'
]

cons_info_fns = [
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_43/cons.info',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_44/cons.info',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_45/cons.info',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_58/cons.info',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_59/cons.info',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_60/cons.info'
]

cons_ep_fns = [
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_43/high.bam.ep',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_44/high.bam.ep',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_45/high.bam.ep',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_58/high.bam.ep',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_59/high.bam.ep',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_60/high.bam.ep'
]

ref_fns = [
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_43/high.ref.fa',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_44/high.ref.fa',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_45/high.ref.fa',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_58/high.ref.fa',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_59/high.ref.fa',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_60/high.ref.fa'
]

read_eps = [
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_43/read.fa.ep',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_44/read.fa.ep',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_45/read.fa.ep',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_58/read.fa.ep',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_59/read.fa.ep',
'/home/gaoy1/circRNA/raw_long_reads/raw_isoCirc_out/nano_60/read.fa.ep'
]

samples = ['Rep1_1', 'Rep1_2', 'Rep1_3', 'Rep2_1', 'Rep2_2', 'Rep2_3']


def get_mp_error_rate(ref_seq, read_seq):
	a = mp.Aligner(seq=read_seq)
	error = -1
	for h in a.map(ref_seq):
		if not h.is_primary: continue
		error = h.NM / (h.NM + mlen + 0.0)
		break
	return error


def raw_error_rate(fig_fn):
	n = 0
	tmp_out = os.path.dirname(os.path.abspath(fig_fn)) + '/raw_cons_error.out'
	for sample, read_fn, ref_fn, info_fn, cons_ep_fn in zip(samples, read_fas, ref_fns, cons_info_fns, cons_ep_fn):
		read_fa = Fasta(read_fn)
		ref_fa = Fasta(ref_fn)
		with open(ref_fn) as ref_fp, open(cons_ep_fn) as cons_ep_fp, open(info_fn) as info_fp, open(tmp_out, 'w') as out_fp:
			out_fp.write('Sample\tCopyNum\tRawError\tConsError\n')
			last_name = ''
			for cons_name in ref_fa.keys():
				read_name = cons_name.rsplit('_')[0]
				if read_name == last_name:
					continue
				copy_num, raw_error, cons_error = 0, 0, 0
				ref_seq = ref_fa[cons_name][:].seq.upper()
				read_seq = read_fa[read_name][:].seq.upper()
				raw_error = get_mp_error_rate(ref_seq, read_seq)
				if raw_error < 0: continue

				for eline in cons_ep_fp:
					if eline.startswith('#'): continue
					ele = iline.rsplit()
					name, error = ele[ep_idx['#READ_NAME']], ele[ep_idx['ERR_RATE']][:-1]/100.0
					if name == cons_name:
						cons_error = error
					else:
						continue

				for sline in info_fp:
					ele = sline.rsplit()
					name, num = ele[info_idx['CONS_NAME']], ele[info_idx['COPY_NUM']]
					if name == cons_name:
						copy_num = int(num)
					else:
						continue
				out_fp.write('{}\t{}\t{}\t{}\n'.format(sample, copy_num, raw_error, cons_error))
				last_name = read_name
				n+=1
				if n== 10:
					sys.exit(1)
	cmd = 'Rscript /home/gaoy1/program/circ_plot/error_rate.R {} {}'.format(ep_fn, fig_fn)
	print(cmd)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print('{} out.fig')
		sys.exit(1)
	raw_error_rate(sys.argv[1])