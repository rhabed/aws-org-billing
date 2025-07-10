#!/bin/sh
export AWS_PROFILE="kloudr-leb"
# format yyyy-mm-dd
start_date=$1
end_date=$2
python aws_billing/aws_billing.py  --str_date $start_date --end_date $end_date --entity lebanon
python aws_billing/aws_billing.py  --str_date $start_date --end_date $end_date --tag_billing_required True --account_name "AWS OMT" --tag_key "Name"
python aws_billing/aws_billing.py  --str_date $start_date --end_date $end_date --tag_billing_required True --account_name "AWS Connect" --tag_key "Name"
python aws_billing/aws_billing.py  --str_date $start_date --end_date $end_date --tag_billing_required True --account_name "AWS CSS Freighters" --tag_key "Name"
python aws_billing/aws_billing.py  --str_date $start_date --end_date $end_date --tag_billing_required True --account_name "AWS CSS Providers" --tag_key "Name"