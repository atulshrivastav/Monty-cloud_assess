# API Deployment
The current code is used to deploy the Lambda and IAM Role. These Lambdas are called by API Gateway to process data. Lambda **store_record** store records to S3/DynamoDB table, another Lambda **get_record** fetches records. Lambda **store_record** is used by API Gateway to perform POST and Lambda **get_record** is used by API Gateway to perform GET operation. A IAM role **monty-cloud-role** is the role used by Lambda to perform API calls.

## Prerequisites
User needs to Create a S3 bucket **monty-cloud-deployment-files**, this S3 bucket stores all the deployment files. In the next step user needs to run **deploy.sh** file. This bash script creates a CloudFormation, **api-pipeline** which internally creates required resources. User can see the progress in Configured account in terminal.
**Note:**
Please keep in mind, the code is developed by keeping **Python3** in mind. Hence, make sure, **Python3** is install on the local machine before execution of **depoly.sh** file.
