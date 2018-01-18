import sys, os
import time

def format_time(fp, header, str):
    fp.write('==' + time.strftime("%H:%M:%S-%b-%d-%Y ", time.localtime()) + '== [' + header + '] ' + str)

def exec_cmd(fp, header, cmd):
    format_time(fp, header, cmd + '\n')
    os.system(cmd)
