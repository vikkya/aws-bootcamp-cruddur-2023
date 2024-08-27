# Week 6 — Deploying Containers

bin/db/test is to check the connection is establised or not in production

bin/flask/health-check is to check if flask server is running or not

create cloudwatch log group cruddur

```
aws logs create-log-group --log-group-name "cruddur"
aws logs put-retention-policy --log-group-name "cruddur" --retention-in-days 1
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

create ecr backend url variable
```
export ECR_BACKEND_FLASK_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/backend-flask"
```

before we push anything to ecr, we need to build docker image
to build docker image
```
docker build -t backend-flask .
```

tag that image we built with latest
```
docker tag backend-flask:latest $ECR_BACKEND_FLASK_URL:latest
```
push that image to repo
```
docker push $ECR_BACKEND_FLASK_URL:latest
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
  --description "Security group for Cruddur ECS cluster" \
  --vpc-id $DEFAULT_VPC_ID \
  --query "GroupId" --output text)
echo $CRUD_CLUSTER_SG
```

add inbound port 80 to the ecs sg
```
aws ec2 authorize-security-group-ingress \
    --group-id $CRUD_CLUSTER_SG \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0
```
create service for ecs cluster
compute option - launch type
launch type  - farget and latest
deployment config
application type - service
family 
backend-flask, version latest
service name - backend-flask
service type
replica
1
service connect - enable it
networking
vpc -default
security group - select the one which we created on above (cruddur-ecs-cluster-sg)
click create service

# Create service via cli
create service-backend-flask.json in aws/json

execute this command to create a service
```
aws ecs create-service --cli-input-json file://aws/json/service-backend-flask.json
```


to get the service started we need below permission, so added it to any new policy or existing policy
```
"ecr:GetAuthorizationToken",
"logs:CreateLogStream",
"logs:PutLogEvents",
"ecr:BatchCheckLayerAvailability",
"ecr:GetDownloadUrlForLayer",
"ecr:BatchGetImage"
```

now we are trying to connect to container with ecs execute-command
```
aws ecs execute-command  \
    --region $AWS_DEFAULT_REGION \
    --cluster cruddur \
    --task 048c6d33d5514527bbe67fd12db17223 \
    --container backend-flask \
    --command "/bin/bash" \
    --interactive
```
arn:aws:ecs:ap-south-1:339713035107:task/cruddur/9af3c3ebdb7a4803bd8c7c96b022ee7b
to run above cmd we need session manager plugin
download for linux [url](https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-debian-and-ubuntu.html)
```
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
```

```
sudo dpkg -i session-manager-plugin.deb
```

## creating load balancer
goto ec2- load balancer
give in all the requires details
create a new security group
cruddur-alb-sg -> inbound rule -> open to HTTP and HTTPS to anywhere
edit the ecs cluster sg inbound rule to connect to above sg
add the cruddur-alb-sg to the loab balancer
create a new target group for backend-flask and frontend-reactjs
on port 4567 and 3000 respectively
add those target-groups to our load balancer
create load balancer


after alb is created
goto cluster sg , edit inbound rule, add a new rule
port 4567, custom tcp, source to alb sg


added this alb to ecs cluster service
check the service-backend-flask.json file to loadBalancer

delete the service if any in our cluster

and run the create-service cli

## Frontend react js - container making

Create a Dockerfile.prod and copy the content into it
create nginx.conf and copy the content into it

cd into frontend
npm run build

## create a repo
```
aws ecr create-repository \
  --repository-name frontend-react-js \
  --image-tag-mutability MUTABLE
```

export the ecr url
```
export ECR_FRONTEND_REACT_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/frontend-react-js"
echo $ECR_FRONTEND_REACT_URL
```

add port 3000 to ecs cluster sg inbound taffic

build image
```
docker build \
--build-arg REACT_APP_BACKEND_URL="http://cruddur-alb-1426206816.ap-south-1.elb.amazonaws.com:4567" \
--build-arg REACT_APP_AWS_PROJECT_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_COGNITO_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_USER_POOLS_ID="ap-south-1_BPT0GRe9s" \
--build-arg REACT_APP_CLIENT_ID="4fa5voa45rvabik984t0kjdu3h" \
-t frontend-react-js \
-f Dockerfile.prod \
.
```
tag the image
```
docker tag frontend-react-js:latest $ECR_FRONTEND_REACT_URL:latest
```

push the image
```
docker push $ECR_FRONTEND_REACT_URL:latest
```

create task defintions folder and frontend-react-js.json
create ecs for frontend with the task-defintion we created
```
aws ecs register-task-definition --cli-input-json file://aws/task-definitions/frontend-react-js.json
```

create frontend service
```
aws ecs create-service --cli-input-json file://aws/json/service-frontend-react-js.json
```

## create docker prod file for backend and build it
before building, login into ecr, in backend-flask directory
```
docker build -f Dockerfile.prod -t backend-flask-prod .
```

docker run
```
docker run --rm \
-p 4567:4567 \
-e FRONTEND_UR="https://3000-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}" \
-e BACKEND_UR="https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}" \
-e OTEL_SERVICE_NAM="backend-flask" \
-e OTEL_EXPORTER_OTLP_ENDPOIN="https://api.honeycomb.io" \
-e OTEL_EXPORTER_OTLP_HEADER="x-honeycomb-team=${HONEYCOMB_API_KEY}" \
-e AWS_XRAY_UR="*4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}*" \
-e AWS_XRAY_DAEMON_ADDRES="xray-daemon:2000" \
-e AWS_DEFAULT_REGIO="${AWS_DEFAULT_REGION}" \
-e AWS_ACCESS_KEY_I="${AWS_ACCESS_KEY_ID}" \
-e AWS_SECRET_ACCESS_KE="${AWS_SECRET_ACCESS_KEY}" \
-e ROLLBAR_ACCESS_TOKE="${ROLLBAR_ACCESS_TOKEN}" \
-e AWS_COGNITO_USER_POOL_I="${AWS_COGNITO_USER_POOL_ID}" \
-e AWS_COGNITO_USER_POOL_CLIENT_I="${AWS_COGNITO_USER_POOL_CLIENT_ID}" \
-e CONNECTION_UR="postgresql://postgres:password@db:5432/cruddur" \
-e AWS_ENDPOINT_UR="http://dymanodb-local:8000" \
-it backend-flask-prod
```

## create docker prod file for frontend and build it
before building, login into ecr, in frontend-react-js directory
```
docker build -f Dockerfile.prod -t frontend-react-js-prod .
```

docker run
```
docker build \
--build-arg REACT_APP_BACKEND_URL="http://cruddur-alb-1426206816.ap-south-1.elb.amazonaws.com:4567" \
--build-arg REACT_APP_AWS_PROJECT_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_COGNITO_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_USER_POOLS_ID="ap-south-1_BPT0GRe9s" \
--build-arg REACT_APP_CLIENT_ID="4fa5voa45rvabik984t0kjdu3h" \
-t frontend-react-js \
-f Dockerfile.prod \
.
```