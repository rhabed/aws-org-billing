#!/bin/sh
source .venv/bin/activate
START_DATE=$1
END_DATE=$2
bash run_leb.sh $1 $2
bash run_961.sh $1 $2
bash run_ksa.sh $1 $2