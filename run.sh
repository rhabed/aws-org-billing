#!/bin/sh
python aws_billing/aws_billing.py  --str_date 2025-02-01 --end_date 2025-03-01 --entity offshore
python aws_billing/aws_billing.py  --str_date 2025-02-01 --end_date 2025-03-01 --tag_billing_required True --account_name "AWS Bentham Science" --tag_key "Name"
python aws_billing/aws_billing.py  --str_date 2025-02-01 --end_date 2025-03-01 --tag_billing_required True --account_name "AWS Bentham Science" --tag_key "Name" --btsc btsc
python aws_billing/aws_billing.py  --str_date 2025-02-01 --end_date 2025-03-01 --tag_billing_required True --account_name "AWS Bentham Science" --tag_key "Name" --btsc personal    