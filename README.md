# API Deployment
The current code is used to deploy the API Gateway. Three Lambdas are created by CFN stack. These Lambdas are called by API Gateway to process data. Lambda **store_record** store records to S3/DynamoDB table, another Lambda **get_record** fetches records. Lambda **store_record** is used by API Gateway to perform POST and Lambda **get_record** is used by API Gateway to perform GET operation. A IAM role **monty-cloud-role** is the role used by Lambda to perform API calls. One more Lambda **deploy_api** creates API Gateway CloudFormation Stack **monty-cloud-get-api-gateway**. This stack creates REST API along with required IAM Role used by API Gateway.

## Prerequisites
**Note:** Please keep in mind, the code is developed by keeping **Python3** in mind. Hence, make sure, **Python3** is install on the local machine before execution of **depoly.sh** file. Before validating the API, user needs to create log source. User also needs to create a DynamoDB table **Montycloudstore**. A S3 bucket should also be created by the name of **montycloudstorage**. As part of the Log Source, User can create a MS AD in AWS account and enable the log forwarding to any log group. After this, user needs to **enable subscription** for that particular Log Group and subscribe to the lambda, **store_record**. Since I was unaware of your organisation limitation on AWS resource creation hence **enable subscription** step is left manual. Also creation of MS AD in AWS takes 20-30 mins, hence I would suggest to **enable subscription** for any of the log group rather than creating MS AD.

## Steps

 - User needs to Create a S3 bucket **monty-cloud-deployment-files**, this S3 bucket stores all the deployment files.
 - In the next step user needs to run **deploy.sh** file. This bash script creates a CloudFormation, **api-pipeline** which internally creates required resources for API Gateway. User can see the progress in Configured account in terminal.
 - As soon as the **api-pipeline** creation completes, user should go to AWS Lambda console and search for Lambda **deploy_api**
 - Once the Lambda is found, user needs to pass current account number and region as input. The format of input should be in below pattern:
 - `{"account_number": "", "region": "us-east-2"}` User needs to pass account number and region in which stack is supposed to be created. Please keep all the values in quote.
 - After saving the Lambda inputs, click on **Test** and wait for Lambda execution to complete.
 - Once the execution the completed, user can logon to **Cloudformation** console and search for the Cloudformation, **monty-cloud-get-api-gateway**. This Cloudformation contains list of created resources. Here itself, user can find the **Physical ID** of **monty-cloud-get-api** API Gateway.
 - User can directly hit the API using REST Client and validate the response.
