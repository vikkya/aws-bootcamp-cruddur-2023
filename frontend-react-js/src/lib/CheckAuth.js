import { getCurrentUser, fetchUserAttributes  } from 'aws-amplify/auth';

const getCurrentUserInfo = async () => {
    const {
      username,
      userId: id
    } = await getCurrentUser();
  
    const attributes = await fetchUserAttributes();
  
    return {
      id,
      username,
      attributes
    };
}

const checkAuth = async (setUser) => {
    getCurrentUserInfo()
    .then((cognito_user) => {
        setUser({
          display_name: cognito_user.attributes.name,
          handle: cognito_user.attributes.preferred_username,
        })
    })
    .catch((err) => console.log(err));
};

export default checkAuth;