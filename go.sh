#!/bin/bash
#

# ===========================================
# Parameters for Sun Grid Engine submition
# ============================================

# Name of job
#$ -N fbsearch

# Shell to use
#$ -S /bin/bash

# All paths relative to current working directory
#$ -cwd

# List of queues
# #$ -q serial.q
#$ -q 'nlp-amd,serial.q,inf.q,eng-inf_parallel.q'

# Define parallel environment for multicore processing
#$ -pe openmp 2

# Send mail to. (Comma separated list)
#$ -M dc34@sussex.ac.uk

# When: [b]eginning, [e]nd, [a]borted and reschedules, [s]uspended, [n]one
#$ -m beas

# Validation level (e = reject on all problems)
#$ -w e

# Merge stdout and stderr streams: yes/no
#$ -j yes

module add jdk/1.7.0_51_openjdk
module add python

echo 'Beginning experiment'

echo $TMPDIR

# du -h $TMPDIR
# df -h
# ls -lh /local/scratch/

trap "pkill virtuoso" SIGHUP SIGINT SIGTERM

cd /home/d/dc/dc34/scratch/sempre/
./scripts/virtuoso start /home/d/dc/dc34/scratch/sempre/lib/freebase/93.exec/vdb 3093
cd /home/d/dc/dc34/scratch/fbs/fbsearch/
/home/d/dc/dc34/scratch/fbs/bin/python -m fbsearch.cachedoracle

pkill virtuoso

echo 'Experiment complete'

