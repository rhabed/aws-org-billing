from classes import BillingItem
import boto3
import decimal
import os
from boto3.dynamodb.conditions import Attr

region_name = os.getenv("REGION_NAME")
if not region_name:
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
else:
    dynamodb = boto3.resource('dynamodb', region_name=region_name)
if not dynamodb:
    raise Exception("Could not connect to dynamodb")
 

def insert_in_db(item: BillingItem, table_name: str):
    table = dynamodb.Table(table_name)
    response = table.put_item(Item=item.dict())
    print("Item put successfully:", response)
