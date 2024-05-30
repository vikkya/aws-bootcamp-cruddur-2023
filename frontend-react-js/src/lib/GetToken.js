import {  fetchAuthSession  } from 'aws-amplify/auth';

const getToken = async() => {
    let token;
    try{
      const { accessToken } = (await fetchAuthSession()).tokens ?? {};
      token = localStorage[`CognitoIdentityServiceProvider.${accessToken['payload']['client_id']}.${accessToken['payload']['username']}.accessToken`]
    }
    catch (error){
      console.log("have to do with token. ")
    }
    return token
}

export default getToken