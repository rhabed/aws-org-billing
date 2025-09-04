#!/bin/sh

export AWS_PROFILE="kloudr-961"
# format yyyy-mm-dd
start_date=$1
end_date=$2
python aws_billing/aws_billing.py  --str_date $start_date --end_date $end_date --entity offshore
python aws_billing/aws_billing.py  --str_date $start_date --end_date $end_date --tag_billing_required True --account_name "AWS Bentham Science" --tag_key "Name"
python aws_billing/aws_billing.py  --str_date $start_date --end_date $end_date --tag_billing_required True --account_name "AWS Bentham Science" --tag_key "Name" --btsc btsc
python aws_billing/aws_billing.py  --str_date $start_date --end_date $end_date --tag_billing_required True --account_name "AWS Bentham Science" --tag_key "Name" --btsc personal

DIRECTORY="./excel_output/offshore"
if [ -d "$DIRECTORY" ]; then
    mv ./excel_output/*.xlsx $DIRECTORY
else
    mkdir $DIRECTORY
    mv ./excel_output/*.xlsx $DIRECTORY
fi