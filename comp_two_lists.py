import sys
from collections import defaultdict as dd


def get_list(in_fn):
    d = dict()
    with open(in_fn) as fp:
        for line in fp:
            ele = line.rstrip()
            d[ele] = 1
    return d


def comp_lists(a_list, b_list):
    n_only_a, n_only_b, n_ovlp = 0, 0, 0
    for i in a_list:
        if i in b_list:
            n_ovlp += 1
            sys.stderr.write('Overlap:\t{}\n'.format(i))
        else:
            n_only_a += 1
            sys.stderr.write('OnlyA:\t{}\n'.format(i))
    for i in b_list:
        if i not in a_list:
            n_only_b += 1
            sys.stderr.write('OnlyB:\t{}\n'.format(i))
    # n_only_b = len(b_list) - n_ovlp
    sys.stdout.write('Overlap:\t{}\nOnly in A: {}\nOnly in B:{} \n'.format(n_ovlp, n_only_a, n_only_b))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('{} A.list B.list > comp.out'.format(sys.argv[0]))
        sys.exit(1)
    a_list = get_list(sys.argv[1])
    b_list = get_list(sys.argv[2])
    comp_lists(a_list, b_list)
