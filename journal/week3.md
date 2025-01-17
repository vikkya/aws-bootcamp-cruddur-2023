# Week 3 — Decentralized Authentication

create user pool in aws cognito
use all deafult options to create the user pool
don't use sms verification, it will be charged. Use email.
attributes to save (name, email)
ap-south-1_50SrUlDyB
cliend_id: 2dqmg2egjpfngdu9cup7njf9nf
if you get any error like this
` Username cannot be of email format, since user pool is configured for email alias`
while creating the user pool, tick email only.

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
create a user in AWS cognito user pool UI.if we create from aws we will get invalid error
after we do the above steps we will get invalid user error to resolve it run the below cmd
` aws cognito admin-set-user-password --user-pool-id <paste pool id> --username <username> --password <password> --permanent `

## SignUpPage.js

` import { autoSignIn, signUp } from 'aws-amplify/auth'; `

```
const onsubmit = async (event) => {
    event.preventDefault();
    setErrors('')
    try {
        const { user } = await signUp({
          username: email,
          password: password,
          options: {
            userAttributes: {
              name: name,
              email: email,
              preferred_username: username,
            },
            autoSignIn: true
          },
        });
        console.log(user);
        window.location.href = `/confirm?email=${email}`
    } catch (error) {
        console.log(error);
        setErrors(error.message)
    }
    return false
  }

```

## ConfirmationPage.js

` import { resendSignUpCode, confirmSignUp } from 'aws-amplify/auth'; `

```
const resend_code = async (event) => {
    setErrors('')
    try {
      await resendSignUpCode({username: email});
      console.log('code resent successfully');
      setCodeSent(true)
    } catch (err) {
      // does not return a code
      // does cognito always return english
      // for this to be an okay match?
      console.log(err)
      if (err.message == 'Username cannot be empty'){
        setErrors("You need to provide an email in order to send Resend Activiation Code")   
      } else if (err.message == "Username/client id combination not found."){
        setErrors("Email is invalid or cannot be found.")   
      }
    }
  }

  const onsubmit = async (event) => {
    event.preventDefault();
    setErrors('')
    try {
      await confirmSignUp({username: email, confirmationCode: code});
      window.location.href = "/signin"
    } catch (error) {
      setErrors(error.message)
    }
    return false
  }

```

## RecoverPage.js

` import { resetPassword, confirmResetPassword } from 'aws-amplify/auth'; `

```
const onsubmit_send_code = async (event) => {
    event.preventDefault();
    setErrors('')
    console.log(username)
    resetPassword({username})
    .then((data) => setFormState('confirm_code') )
    .catch((err) => setErrors(err.message) );
    return false
  }

  const onsubmit_confirm_code = async (event) => {
  event.preventDefault();
  setErrors('')
  if (password == passwordAgain){
    confirmResetPassword({username, confirmationCode: code, newPassword: password})
    .then((data) => setFormState('success'))
    .catch((err) => setErrors(err.message) );
  } else {
    setErrors('Passwords do not match')
  }
  return false
}

```

## improve Cruddur UI with material UI
` npm install @mui/material @emotion/react @emotion/styled @mui/icons-material @fontsource/roboto --save `