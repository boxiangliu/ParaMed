#!/usr/bin/env python

from __future__ import print_function
import os
import re
import sys
import time
import glob
import subprocess
import logging

starttime = time.time()

onehourseconds = 60 * 60

partitiontime = {}
partitiontime["1080Ti_short"] = 1.8
partitiontime["1080Ti_slong"] = 6 * 24
partitiontime["1080Ti"] = 12
partitiontime["1080Ti_spec"] = 24 + 12
partitiontime["P100"] = 12
partitiontime["V100"] = 12
partitiontime["V100_DGX"] = 12
partitiontime["2080Ti"] = 12


partitiontime["TitanXx8_short"] = 1.8
partitiontime["TitanXx8_slong"] = 6 * 24
partitiontime["TitanXx8"] = 12

partitiontime["M40x8_short"] = 1.8
partitiontime["M40x8_slong"] = 6 * 24
partitiontime["M40x8"] = 12


excludepool = ["159"]


'''
1080Ti 2 smbmul2gpus "train.py -data data_256/2M.bpe256.zh2en.tt4  -save_model multiplegpus/2gpus_smbatch/model -gpuid 0 1 -layers 6 -heads 8 -transformer_ff 2048 -rnn_size 512 -word_vec_size 512 -encoder_type transformer -decoder_type transformer -position_encoding -max_generator_batches 32 -dropout 0.1 -batch_size 1024 -batch_type tokens -normalization tokens -accum_count 4 -optim adam -adam_beta2 0.997 -decay_method noam -warmup_steps 16000 -learning_rate 2 -max_grad_norm 0 -parametersm_init 0 -parametersm_init_glorot -label_smoothing 0.1 -train_steps 1000000" multiplegpus/2gpus_smbatch/log.2gpusmb.txt
'''

partition_name = sys.argv[1]
num_GPU = sys.argv[2]
job_name = sys.argv[3]
cmd = sys.argv[4]
# excludepool = sys.argv[5]
runningtime = partitiontime[partition_name]


if "Titan" in partition_name or "M40" in partition_name or "P100" in partition_name:
    numcpuspergpu = 1
elif partition_name == "1080Ti_dbg" or partition_name == "1080Ti_special":
    numcpuspergpu = 8
else:
    numcpuspergpu = 1

num_CPU = numcpuspergpu * num_GPU


# Parse arguments:
pattern = "-([A-Za-z\_]*)\ ([A-Za-z\_\ 0-9\/\.]*)"

parameters = dict(re.findall(pattern, cmd))
parameters = dict([(k.strip(), v.strip()) for k, v in parameters.items()])

save_model = parameters["save_model"]
save_dir = os.path.dirname(save_model)
print("Command: {}".format(cmd))
print("Save_dir: {}".format(save_dir))

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',  # format='%(asctime)s %(levelname)-8s %(message)s',
                    filename=save_dir + "/sub_log." + job_name + '.txt',
                    level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S')
logging.info(cmd)


def checkstate(job_name):
    jobinfo = subprocess.check_output(
        ["squeue", "-u", "boxiang", "-n", job_name])
    jobid = re.findall(r'\b\d+\b', str(jobinfo))[0]
    commandslurm = ["scontrol", "show", "job", jobid]
    output = subprocess.check_output(commandslurm).decode("utf-8")
    alljobinfo = dict(re.findall("([A-Za-z/]*)=([^ \t\n]*)", output))
    return alljobinfo['JobState'], jobid, alljobinfo["NodeList"]


while True:
    timediff = (time.time() - starttime)
    logging.info("full running hours: %6.2f for job: %s " %
                 (timediff / 3600, job_name))

    try:
        latest_checkpoint = max(glob.iglob(
            save_model + '_step_*.pt'), key=os.path.getctime)
        trainfrom = " -train_from " + latest_checkpoint
        new_cmd = cmd + trainfrom
        print 
        logging.info("restart %s and load previouse model from %s" %
                     (job_name, latest_checkpoint))

        slurm_com = "sbatch --gres=gpu:%s --ntasks=1 "\
         "--cpus-per-task %s --partition=%s --job-name=%s "\
         "--wrap \"%s \" --output=%s/slurm_log.%s.txt;" % (
            str(num_GPU), str(num_CPU), partition_name, \
            job_name, new_cmd, save_dir, job_name)

        print("Slurm command: {}".format(slurm_com))
        os.system(slurm_com)

    except:
        new_cmd = cmd
        logging.info("restart job: %s from scratch" % (job_name))
        slurm_com = "sbatch --gres=gpu:%s --ntasks=1 "\
         "--cpus-per-task %s --partition=%s --job-name=%s "\
         "--wrap \"%s \" --output=%s/slurm_log.%s.txt;" % (
            str(num_GPU), str(num_CPU), partition_name, \
            job_name, new_cmd, save_dir, job_name)

        print("Slurm command: {}".format(slurm_com))
        os.system(slurm_com)

    time.sleep(10)

    # check if everything works fine
    try:
        jobstate, jobid, nodelist = checkstate(job_name)
        starttiming = True
    except:
        logging.warning(
            "submission error for job: %s and restart in 20 seconds." % (job_name))
        time.sleep(20)
        continue

    # start timing only after "RUNNING"
    while jobstate != "RUNNING":
        logging.info("job: %s is waiting for start in 30 seconds" % (job_name))
        try:
            jobstate, jobid, nodelist = checkstate(job_name)
            logging.info("job name is: %s, and job status is %s and jobid is %s " % (
                job_name, jobstate, jobid))
            time.sleep(30)
            starttiming = True
        except:
            starttiming = False
            break

    if starttiming:
        jobstarttime = time.time()
        while time.time() - jobstarttime < onehourseconds * runningtime + 120:
            try:
                jobstate, jobid, nodelist = checkstate(job_name)
                # only print this log for the first 15 mins.
                if time.time() - jobstarttime < 60 * 15:
                    logging.info("waiting for job: %s to finish in %d hours on machine %s with %s with %s GPU(s) and %s CPU(s)" % (
                        job_name, runningtime, nodelist, partition_name, num_GPU, num_CPU))
                time.sleep(60)
            except:
                logging.warning(
                    "submission error for job: %s and restart in 5 seconds." % (job_name))
                time.sleep(5)
                break
    else:
        logging.warning(
            "submission error for job: %s and restart in 10 seconds." % (job_name))
        time.sleep(10)
        continue
