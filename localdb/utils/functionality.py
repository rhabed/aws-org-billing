from classes import BillingItem
import boto3
import os

dynamodb = boto3.resource('dynamodb', region_name='localhost')

def insert_in_db(item: BillingItem, table_name: str): 
    table = dynamodb.Table(table_name)
    json_item = item.model_dump_json()

    response = table.put_item(Item=json_item)
    print("Item put successfully:", response)