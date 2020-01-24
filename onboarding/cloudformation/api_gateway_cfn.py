from troposphere import Ref, Template, GetAtt
from troposphere.apigateway import Deployment, Stage, MethodSetting, \
    Integration, Resource, MethodResponse, \
    EndpointConfiguration, RestApi, Method
from troposphere.awslambda import Permission
from troposphere.iam import ManagedPolicy, Role


class CreateAPIGatewayCFN:
    def __init__(self, account_number, region):
        self.uri = 'arn:aws:apigateway:{}:lambda:path/2015-03' \
                   '-31/functions/arn:aws:lambda:{}:' \
                   '{}:function:get_data/invocations'
        self.account_number = account_number
        self.region = region
        self.template = Template()

    def initiate_api_gateway_creation(self):
        self.template.set_version('2010-09-09')
        self.template.set_description('Creates a API Gateway which is '
                                      'used to get data from dynamoDB.')

        role = self.template.add_resource(Role(
            'RootRole',
            RoleName="monty-cloud-api-role",
            Path='/',
            AssumeRolePolicyDocument={
              "Version": "2012-10-17",
              "Statement": [
                {
                  "Action": [
                    "sts:AssumeRole"
                  ],
                  "Effect": "Allow",
                  "Principal": {
                    "Service": [
                        "apigateway.amazonaws.com",
                        "lambda.amazonaws.com",
                        "dynamodb.amazonaws.com"
                    ]
                  }
                }
              ]
            }
        ))

        self.template.add_resource(ManagedPolicy(
            'RolePolicies',
            ManagedPolicyName='api-gw-policy',
            Description='This policy is used for the DynamoDB table ',
            PolicyDocument={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": [
                            "dynamodb:*",
                            "lambda:*",
                            "s3:*"
                        ],
                        "Resource": [
                            "arn:aws:dynamodb:*:*:table/*",
                            "arn:aws:lambda:*:*:function:*"
                        ],
                        "Effect": "Allow"
                    }
                ]
            },
            Roles=[Ref(role)]
        ))

        name = self.template.add_resource(RestApi(
            'restApiName',
            Name='monty-cloud-get-api',
            Description='Monty Cloud API Gateway',
            EndpointConfiguration=EndpointConfiguration(
                Types=['REGIONAL']
            )
        ))

        self.template.add_resource(Permission(
            "lambdaApiGatewayInvoke",
            Action="lambda:InvokeFunction",
            FunctionName="arn:aws:lambda:{}:{}:function:"
                         "get_data".format(self.region,
                                           self.account_number),
            Principal="apigateway.amazonaws.com",
            SourceArn="arn:aws:execute-api:{}:{}:*/*"
                      "/GET/get-details".format(self.region,
                                                self.account_number)
        ))

        get_api_resource = self.template.add_resource(
            Resource(
                'restApiGetDetailsResource',
                RestApiId=Ref(name),
                ParentId=GetAtt(name, 'RootResourceId'),
                PathPart='get-details',
                DependsOn=name
            ))

        get_api_method = self.template.add_resource(Method(
            'restApiGetDetailsMethod',
            AuthorizationType='None',
            ApiKeyRequired=False,
            HttpMethod='GET',
            ResourceId=Ref(get_api_resource),
            RestApiId=Ref(name),
            Integration=Integration(
                Type='AWS_PROXY',
                IntegrationHttpMethod='POST',
                Uri=self.uri.format(self.region, self.region,
                                    self.account_number),
                Credentials=GetAtt(role, "Arn")

            ),
            MethodResponses=[MethodResponse(
                StatusCode='200',
                ResponseModels={'application/json': 'Empty'})],
            DependsOn=get_api_resource
        ))

        deployment = self.template.add_resource(Deployment(
            'restApiDeployment',
            RestApiId=Ref(name),
            DependsOn=[get_api_method]
        ))

        self.template.add_resource(Stage(
            'restApiStage',
            DeploymentId=Ref(deployment),
            Description='Prod Stage',
            MethodSettings=[
                MethodSetting(ResourcePath='/get-details',
                              HttpMethod='GET')
            ],
            RestApiId=Ref(name),
            StageName='prod'
        ))

        return self.template.to_yaml()
