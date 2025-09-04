#!/bin/sh
export AWS_PROFILE="kloudr-ksa"
# format yyyy-mm-dd
start_date=$1
end_date=$2
python aws_billing/aws_billing.py  --str_date $start_date --end_date $end_date --entity ksa


DIRECTORY="./excel_output/ksa"
if [ -d "$DIRECTORY" ]; then
    mv ./excel_output/*.xlsx $DIRECTORY
else
    mkdir $DIRECTORY
    mv ./excel_output/*.xlsx $DIRECTORY
fi