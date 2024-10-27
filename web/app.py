from flask import Flask, render_template, request
import boto3
from boto3.dynamodb.conditions import Attr
import datetime

app = Flask(__name__)
# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:8000")
table = dynamodb.Table("kloudrAWSBillingInfo")


def get_start_and_end_dates():
    today = datetime.date.today()
    first_day_of_current_month = today.replace(day=1)

    if today.month == 1:
        last_month = 12
        last_year = today.year - 1
    else:
        last_month = today.month - 1
        last_year = today.year

    first_day_of_last_month = datetime.date(last_year, last_month, 1)

    return str(first_day_of_last_month), str(first_day_of_current_month)


@app.route("/")
def index():
    # Get data from billing_table
    response = table.scan()
    print(response)
    items = response["Items"]
    return render_template("index.html", items=items)


@app.route("/filter", methods=["POST"])
def filter():
    start_date, end_date = get_start_and_end_dates()
    # Get filter values from form
    column1_filter = request.form["column1_filter"]
    column2_filter = request.form["column2_filter"]
    # Filter data from billing_table
    if column1_filter and column2_filter:
        response = table.scan(
            FilterExpression=Attr("aws_account_name").contains(column1_filter)
            & Attr("aws_service").contains(column2_filter)
            & Attr("start_date").equals(start_date)
            & Attr("end_date").equals(end_date)
        )
    elif column1_filter:
        response = table.scan(
            FilterExpression=Attr("aws_account_name").contains(column1_filter)
            & Attr("start_date").equals(start_date)
            & Attr("end_date").equals(end_date)
        )
    elif column2_filter:
        response = table.scan(
            FilterExpression=Attr("aws_service").contains(column2_filter)
            & Attr("start_date").equals(start_date)
            & Attr("end_date").equals(end_date)
        )
    else:
        response = table.scan()
    items = response["Items"]
    return render_template("index.html", items=items)


@app.route("/total_cost_per_account", methods=["POST"])
def total_cost():
    # Get total cost from billing_table
    start_date, end_date = get_start_and_end_dates()
    account_name = request.form["aws_account_filter"]
    total_cost = 0
    response = table.scan()
    items = response["Items"]
    for item in items:
        if (
            item["aws_account_name"] == account_name
            and item["start_date"] == start_date
            and item["end_date"] == end_date
        ):
            total_cost += item["cost"]

    res_table = [
        {
            "aws_account_name": account_name,
            "total_cost": total_cost,
            "start_date": start_date,
            "end_date": end_date,
        }
    ]

    return render_template("total.html", items=res_table)


if __name__ == "__main__":
    app.run(debug=True)
