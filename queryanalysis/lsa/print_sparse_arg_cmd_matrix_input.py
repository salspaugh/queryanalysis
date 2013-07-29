#!/usr/bin/env python

import json
import numpy as np

#ARGS_CMDS_CNTS_LIST = "/data/deploy/boss/data.storm/svd/arg_cmd_cnts.json"
#
#CMDS_IDXS_LIST = "/data/deploy/boss/data.storm/svd/cmds_idx_list.json"
#
#SPARSE_MATRIX = "/data/deploy/boss/data.storm/svd/sparse_arg_cmd_matrix_tfidf.csv"
#MATRIX_ROW_LABELS = "/data/deploy/boss/data.storm/svd/arg_row_matrix_labels_tfidf.csv"
#MATRIX_COL_LABELS = "/data/deploy/boss/data.storm/svd/cmd_col_matrix_labels_tfidf.csv"

ARGS_CMDS_CNTS_LIST = "/data/deploy/boss/data.storm/svd/arg_usage_cnts.json"

CMDS_IDXS_LIST = "/data/deploy/boss/data.storm/svd/usage_idx_list.json"

SPARSE_MATRIX = "/data/deploy/boss/data.storm/svd/sparse_arg_usage_matrix_tfidf.csv"
MATRIX_ROW_LABELS = "/data/deploy/boss/data.storm/svd/arg_row_matrix_labels_tfidf.csv"
MATRIX_COL_LABELS = "/data/deploy/boss/data.storm/svd/usage_col_matrix_labels_tfidf.csv"

def main():
    args_cmds = read_args_cmds()
    cmds_idxs, max_term_freqs = read_cmds_idxs()
    row_idx = 0
    sparse_matrix = open(SPARSE_MATRIX, 'w')
    row_labels = open(MATRIX_ROW_LABELS, 'w')
    sparse_matrix.write(','.join(["row", "col", "cnt"]))
    sparse_matrix.write('\n')
    num_cmds = len(cmds_idxs)
    for (arg, cmds) in args_cmds:
        arg_cmd_freq = len(cmds)
        print arg_cmd_freq
        for (cmd, cnt) in cmds:
            col_idx = cmds_idxs[cmd]
            maxf = max_term_freqs[cmd]
            
            #adjusted_cnt = np.log(cnt+1)*np.log(float(num_cmds)/float(arg_cmd_freq)) # tfidf
            #adjusted_cnt = 1*np.log(float(num_cmds)/float(arg_cmd_freq)) # tfidf
            
            tf = .5 + ((.5 * float(cnt))/float(maxf))
            #tf = .85 + ((.15 * float(1.))/float(maxf))
            #tf = float(cnt)/float(maxf)
            idf = np.log(float(num_cmds)/float(arg_cmd_freq))
            adjusted_cnt = tf*idf

            #print cnt, adjusted_cnt
            sparse_matrix.write(','.join([str(row_idx), str(col_idx), str(adjusted_cnt)]))
            sparse_matrix.write('\n')
            row_labels.write(json.dumps((row_idx, arg)))
            row_labels.write('\n')
        row_idx += 1
    sparse_matrix.close()
    row_labels.close()
    col_labels = open(MATRIX_COL_LABELS, 'w')
    for (cmd, idx) in cmds_idxs.iteritems():
        col_labels.write(json.dumps((idx, cmd)))
        col_labels.write('\n')
    col_labels.close()

def read_args_cmds():
    args_cmds = []
    with open(ARGS_CMDS_CNTS_LIST) as datafile:
        for line in datafile.readlines():
            args_cmds.append(json.loads(line))
    return args_cmds   

def read_cmds_idxs():
    cmds = {}
    max_term_freqs = {}
    with open(CMDS_IDXS_LIST) as datafile:
        for line in datafile.readlines():
            (cmd, f, idx) = json.loads(line)
            cmds[cmd] = idx
            max_term_freqs[cmd] = f
    return cmds, max_term_freqs

main()
