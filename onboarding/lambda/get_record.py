from json import dumps

import boto3
from botocore.exceptions import ClientError
from onboarding import logger


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
        logger.info(event.get('queryStringParameters', '####'))
        logger.info("with querystring")
        timestamp = event.get('queryStringParameters')['time']
        try:
            response = client.get_item(TableName='Montycloudstore',
                                       Key={'timestamp': {
                                           'N': timestamp}})
        except ClientError as e:
            logger.info(e.response['Error']['Message'])
        if response.get('Item', ''):
            item = response['Item']
            logger.info("GetItem succeeded:")
            logger.info(dumps(item, indent=4))
            resp = dumps(item, indent=4)
            return_response['body'] = resp
            return return_response
        # if not avail in db will try to find in s3
        FILE_TO_READ = '{s3_file_name}_Montycloudadlog.json'
        client = boto3.client('s3')
        logger.info(FILE_TO_READ.format(s3_file_name=timestamp))
        file_name = FILE_TO_READ.format(s3_file_name=timestamp)
        result = client.get_object(Bucket=BUCKET, Key=file_name)
        logger.info(result["Body"].read())
    return return_response
