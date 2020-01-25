#!/bin/bash

BPE_Path='/mnt/home/baigong/subword-nmt/subword_nmt'

Train="corpus"
Dev="newsdev2017.tc"
Test="newstest2017.tc"

SRC="zh"
TGT="en"

BPE_op=16000

# bpe
#learn BPE dictionary
$BPE_Path/learn_bpe.py -s $BPE_op < $Train.$SRC > bpe_dict.$SRC 
$BPE_Path/learn_bpe.py -s $BPE_op < $Train.$TGT > bpe_dict.$TGT 

#apply BPE
$BPE_Path/apply_bpe.py -c bpe_dict.$SRC < $Train.$SRC > $Train.bpe.$SRC
$BPE_Path/apply_bpe.py -c bpe_dict.$TGT < $Train.$TGT > $Train.bpe.$TGT
$BPE_Path/apply_bpe.py -c bpe_dict.$SRC < $Dev.$SRC > $Dev.bpe.$SRC
$BPE_Path/apply_bpe.py -c bpe_dict.$TGT < $Dev.$TGT > $Dev.bpe.$TGT
$BPE_Path/apply_bpe.py -c bpe_dict.$SRC < $Test.$SRC > $Test.bpe.$SRC
$BPE_Path/apply_bpe.py -c bpe_dict.$TGT < $Test.$TGT > $Test.bpe.$TGT

