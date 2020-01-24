from onboarding.cloudformation.api_gateway_cfn import \
    CreateAPIGatewayCFN
from onboarding.utils.boto import boto_client
from onboarding.utils.cftemplate import tags
from onboarding.utils.cloudformation import get_stack_status


class DeployAPIGateway:
    def __init__(self, account_number, region):
        self.account_number = account_number
        self.region = region

    @get_stack_status
    def initiate_api_cfn_deployment(self):
        stack_name = 'monty-cloud-get-api-gateway'
        template = CreateAPIGatewayCFN(self.account_number, self.region)
        template = template.initiate_api_gateway_creation()

        return {
            'StackName': stack_name,
            'TemplateBody': template,
            'Tags': tags(stack_name),
            'client': boto_client(self.account_number,
                                  'cloudformation', self.region),
            'alter_cfn': True
        }


def lambda_handler(event, context):
    api = DeployAPIGateway(event['account_number'], event['region'])
    return api.initiate_api_cfn_deployment()
