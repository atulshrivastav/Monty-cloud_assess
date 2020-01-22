#!/usr/bin/env bash

set -ex

if [[ "$1" == "-h" ]]; then
  echo "Usage: `basename $0` [bucket] [stack] [organization]

  where:
    bucket       the bucket name to upload the packaged lambdas
    stack        the name of the stack to be created or updated
    organization the organization the aws cicd account is associated with
  "
  exit 0
fi

BUCKET=${1:-monty-cloud-deployment-files}
STACK_NAME=${2:-api-pipeline}
OU=${3:-monty-cloud}

# Ensure dist directory exists
rm -rf dist
mkdir -p dist
(cd dist)
pip3 install -r requirements.txt -t dist/

# Create function archives
(cd onboarding && zip -r ../dist/api_pipeline.zip *.py -x "*.pyc" -x "*pycache*")
(zip -r -u dist/api_pipeline.zip onboarding/)
(cd dist && zip -r -u api_pipeline.zip * -x "*.zip")

# Upload package
aws cloudformation package \
    --template-file onboarding/templates/api-pipeline.yml \
    --s3-bucket ${BUCKET} \
    --output-template-file dist/template.yml

# Deploy pipeline
aws cloudformation deploy \
    --template-file dist/template.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides pProjectName=${OU}-assessment \
    --s3-bucket ${BUCKET} \
    --capabilities CAPABILITY_NAMED_IAM
