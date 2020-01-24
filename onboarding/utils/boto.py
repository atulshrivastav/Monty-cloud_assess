import boto3

from onboarding import logger


def boto_client(account_id, service_name, region):
    """
        Creates boto3 client for provided service.

        Args:
        service_name : string
            Name of the service.
        primary_region : string
            Name of the region.

        Returns:
        client
            Returns the boto3 client.
        """
    logger.info('Creating boto3 client for account_id: {}, '
                'service_name: {}'.format(account_id, service_name))
    return boto3.client(service_name, region_name=region)
