# Week 3 — Decentralized Authentication

create user pool in aws cognito
use all deafult options to create the user pool
don't use sms verification, it will be charged. Use email.
attributes to save (name, email)

after cognito setup in aws account, setup amplify  in your code

cd into fronten-react-js
do `npm i aws-amplify --save`

goto app.js
copy the code and paste in app.js `import { Amplify } from 'aws-amplify'`

```
Amplify.configure({
  "AWS_PROJECT_REGION": process.env.REACT_AWS_PROJECT_REGION,
  "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
  "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
  "aws_user_pools_web_client_id": process.env.REACT_APP_CLIENT_ID,
  "oauth": {},
  Auth: {
    // We are not using an Identity Pool
    // identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID, // REQUIRED - Amazon Cognito Identity Pool ID
    region: process.env.REACT_AWS_PROJECT_REGION,           // REQUIRED - Amazon Cognito Region
    userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,         // OPTIONAL - Amazon Cognito User Pool ID
    userPoolWebClientId: process.env.REACT_APP_AWS_USER_POOLS_WEB_CLIENT_ID,   // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
  }
});```


there are lot of changes to aws-amplify v6
go through the documentation
https://docs.amplify.aws/javascript/build-a-backend/auth/auth-migration-guide