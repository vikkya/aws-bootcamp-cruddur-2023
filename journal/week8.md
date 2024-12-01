# Week 8 — Serverless Image Processing

this week we work with aws cdk

create a folder tumbing-serverless-cdk to put all our code in one place
cd into the folder
npm install aws-cdk -g

cdk inti app --language typescript

choose a language of your type, to follow along I used typescript

our main entry point would be lib/*.ts (in the example thumbing-serverless-cdk-stack.ts)

make the required changes, like creating function  for bucket, etc

cdk synth cmd gives us the yaml explanation of our impletementation

to bootstrap your cdk use cdk bootstrap cmd, this will create all the necessary services in coludFormation
cdk bootstrap "aws://aws_account_id/aws_region_ur_using"

to deploy the cdk, run
cdk deploy to deploy the stack in cloudformation
cdk destory to delete everything with respect to that template
