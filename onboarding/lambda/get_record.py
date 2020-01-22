from json import loads, load, dumps
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


def read_config():
    with open('./conf.json') as fil:
        fil = load(fil)
        storage_type = fil.get('config')['store_type']
        s3_location = fil.get('S3')['name']
        db_location = fil.get('DB')['name']

def lambda_handler(event, context):
    # TODO implement
    return_response = {
                        'statusCode': "200",
                        'body': "No Record Found!"
                      }
    #DB instance
    client = boto3.client("dynamodb")
    #S3 instance
    BUCKET = 'montycloudstorage'
    
    #Main part
    if event.get('queryStringParameters', ''):
        print(event.get('queryStringParameters', '####'))
        print("with querystring")
        timestamp = event.get('queryStringParameters')['time']
        try:
            response = client.get_item(TableName='Montycloudstore', Key={'timestamp':{'N':timestamp}})
            # response = table.get_item(
            #     Key={
            #         'timestamp': timestamp 
            #     }
            # )
        except ClientError as e:
            print(e.response['Error']['Message'])
        if response.get('Item', ''):
            item = response['Item']
            print("GetItem succeeded:")
            print(dumps(item, indent=4))
            resp = dumps(item, indent=4)
            
            return_response['body'] = resp
            return return_response
        # if not avail in db will try to find in s3
        FILE_TO_READ = '{s3_file_name}_Montycloudadlog.json'
        client = boto3.client('s3')
        print(FILE_TO_READ.format(s3_file_name=timestamp))
        print("$$$$$$$$$$$$")
        file_name = FILE_TO_READ.format(s3_file_name=timestamp)
        result = client.get_object(Bucket=BUCKET, Key=file_name)
        print(result["Body"].read())
        
    return return_response
        