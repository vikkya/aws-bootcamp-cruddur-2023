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
  Auth: {
    Cognito: {
      // We are not using an Identity Pool
      // identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID, // REQUIRED - Amazon Cognito Identity Pool ID
      region: process.env.REACT_APP_AWS_PROJECT_REGION,           // REQUIRED - Amazon Cognito Region
      userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,         // OPTIONAL - Amazon Cognito User Pool ID
      userPoolClientId: process.env.REACT_APP_CLIENT_ID,   // OPTIONAL - Amazon Cognito Web Client ID 
    }
  }
});
```

there are lot of changes to aws-amplify v6
go through the documentation
https://docs.amplify.aws/javascript/build-a-backend/auth/auth-migration-guide

## HomeFeedPage.js

copy paste below code

` import { getCurrentUser } from 'aws-amplify/auth'; `

```
const checkAuth = async () => {
    getCurrentUser({
      // Optional, By default is false. 
      // If set to true, this call will send a 
      // request to Cognito to get the latest user data
      bypassCache: false 
    })
    .then((user) => {
      console.log('user',user);
      return getCurrentUser()
    }).then((cognito_user) => {
        setUser({
          display_name: cognito_user.attributes.name,
          handle: cognito_user.attributes.preferred_username
        })
    })
    .catch((err) => console.log(err));
  };
  ```

  ## SigninPage.js

  ` import { signIn } from 'aws-amplify/auth'; `

  ```
  const onsubmit = async (event) => {
    setErrors('')
    event.preventDefault();
    signIn({username:email, password})
      .then(user => {
        localStorage.setItem("access_token", user.signInUserSession.accessToken.jwtToken)
        window.location.href = "/"
      })
      .catch(error => { 
        if (error.code == 'UserNotConfirmedException') {
          window.location.href = "/confirm"
        }
        setErrors(error.message)
        });
    return false
  }
  ```

## ProfileInfo.js

` import { signOut } from 'aws-amplify/auth'; `

```
const signOutHandle = async () => {
    try {
        await signOut({ global: true });
        window.location.href = "/"
    } catch (error) {
        console.log('error signing out: ', error);
    }
  }
```
