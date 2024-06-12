# Week 6 — Deploying Containers

bin/db/test is to check the connection is establised or not in production

bin/flask/health-check is to check if flask server is running or not

create cloudwatch log group cruddur/fargate-cluster

```
aws logs create-log-group --log-group-name cruddur/fargate-cluster
aws logs put-retention-policy --log-group=name cruddur/fargate-cluster --retentaion-in-days 1
```

create ECS fargate cluster 
```
aws ecs create-cluster --cluster-name cruddur --service-connect-defaults namespace=cruddur
```

to work with AWS ECS we need to create ECR for each service. a repo for backend, react, python

create repo for python
```
aws ecr create-repository --repository-name cruddur-python --image-tag-mutability MUTABLE
```

once the repo is created we can push the docker images to this repo

first login into the ecr in cli

```
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
```
export python ecr url to system variable
```
export ECR_PYTHON_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/cruddur-python"
```

pull the required python version
```
docker pull python:3.10-slim-buster
```

tag the python version same in ecr as well
```
docker tag python:3.10-slim-buster $ECR_PYTHON_URL:3.10-slim-buster
```

push the image to ecr
```
docker push $ECR_PYTHON_URL:3.10-slim-buster
```

after python image is created and pushed to ecr, we are going to do the same for backend-flask

```
aws ecr create-repository --repository-name backend-flask --image-tag-mutability MUTABLE
```

and now we create a service to our ecs cluster, and to create a service we need a task definition
- service: will run continuously
- task: will run once and ends it's execution
- task definitions: are services which will run all the time

to create a task definition, we need execution role and task role IAM and before even IAM we need to create parameters in systems management.
task role IAM
```
aws iam create-role --role-name CruddurServiceExecutionRole --assume-role-policy-document file://aws/policy/service-assume-role-execution-policy.json
```

create parameters
```
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_ACCESS_KEY_ID" --value $AWS_ACCESS_KEY_ID
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_SECRET_ACCESS_KEY" --value $AWS_SECRET_ACCESS_KEY
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/CONNECTION_URL" --value $PROD_CONNECTION_URL
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/ROLLBAR_ACCESS_TOKEN" --value $ROLLBAR_ACCESS_TOKEN
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/OTEL_EXPORTER_OTLP_HEADERS" --value "x-honeycomb-team=$HONEYCOMB_API_KEY"
```

add role policy to our role created above
```
aws iam put-role-policy \--policy-name CruddurServiceExecutionPolicy --role-name CruddurServiceExecutionRole --policy-document file://aws/policy/service-execution-policy.json
```

create a task role
```
aws iam create-role \
    --role-name CruddurTaskRole \
    --assume-role-policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[\"sts:AssumeRole\"],
    \"Effect\":\"Allow\",
    \"Principal\":{
      \"Service\":[\"ecs-tasks.amazonaws.com\"]
    }
  }]
}"
```

create policy for task role created above
```
aws iam put-role-policy \
  --policy-name SSMAccessPolicy \
  --role-name CruddurTaskRole \
  --policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[
      \"ssmmessages:CreateControlChannel\",
      \"ssmmessages:CreateDataChannel\",
      \"ssmmessages:OpenControlChannel\",
      \"ssmmessages:OpenDataChannel\"
    ],
    \"Effect\":\"Allow\",
    \"Resource\":\"*\"
  }]
}"
```

attach colud watch full access to task role created above (make sure to not to give full access)
```
aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess --role-name CruddurTaskRole

aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess --role-name CruddurTaskRole

```

create task defintions folder and backend-flask.json
create ecs for backend with the task-defintion we created
```
aws ecs register-task-definition --cli-input-json file://aws/task-definitions/backend-flask.json
```

add deafult vpc id to global variables
```
export DEFAULT_VPC_ID=$(aws ec2 describe-vpcs \
--filters "Name=isDefault, Values=true" \
--query "Vpcs[0].VpcId" \
--output text)
echo $DEFAULT_VPC_ID
```

add cruddur cluster security group
```
export CRUD_CLUSTER_SG=$(aws ec2 create-security-group \
  --group-name cruddur-ecs-cluster-sg \
  --description "Security group for Cruddur ECS ECS cluster" \
  --vpc-id $DEFAULT_VPC_ID \
  --query "GroupId" --output text)
echo $CRUD_CLUSTER_SG
```
