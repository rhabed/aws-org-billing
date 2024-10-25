from classes import BillingItem
import boto3
import json


def insert_in_db(item: BillingItem, table_name: str, region_name: str = None):
    if not region_name:
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    else:
        dynamodb = boto3.resource('dynamodb', region_name=region_name)
    
    if not dynamodb:
        raise Exception("Could not connect to dynamodb")
    else:
        table = dynamodb.Table(table_name)
        breakpoint()
        response = table.put_item(Item=item.dict())
        print("Item put successfully:", response)
