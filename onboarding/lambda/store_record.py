from base64 import b64decode
from gzip import decompress
from json import loads, load, dumps
from onboarding import logger

import boto3


def read_config():
    with open('./conf.json') as fil:
        fil = load(fil)
        storage_type = fil.get('config')['store_type']
        s3_location = fil.get('S3')['name']
        db_location = fil.get('DB')['name']
    return storage_type, s3_location, db_location


def lambda_handler(event, context):
    """
    Method to parse logs coming from AMS CloudWatch log groups.
    Args:
        event: Logs from CloudWatch log groups.
    Returns:
        Returns json data to Firehose.
    """

    record = event.get('awslogs')['data']
    source = ''
    data = ''
    timestamp = ''
    payload = b64decode(record)
    payload = loads(decompress(payload))
    if payload['messageType'] == 'DATA_MESSAGE':
        source = payload['logGroup']
        final_str = ''
        for log_event in payload['logEvents']:
            timestamp = log_event['timestamp']
            final_str = final_str.join(
                [log_event['message'] + '\n'])
        data = final_str

    resp = {
            'timestamp': timestamp,
            'source': source,
            'data': data
           }
    storage_type, s3, db = read_config()
    if not storage_type == 'DB':
        logger.info("s3 insert code")
        file_name = "{time}_{source}.json".format(time=timestamp,
                                                  source=source)
        s3 = boto3.client('s3')
        s3.put_object(Body=bytes(dumps(resp).encode('UTF-8')),
                      Bucket="montycloudstorage", Key=file_name)
        return file_name

    # # store db code
    logger.info("Writing in DB")
    client = boto3.resource('dynamodb')
    table = client.Table('Montycloudstore')
    table.put_item(Item=resp)
    logger.info("Data Inserted.")
