
from oauth2_provider.models import AccessToken,RefreshToken
import uuid
import hashlib
from datetime import datetime, timedelta
from app.conf import base as settings
import jwt
import time
from calendar import timegm

def returnMyToken(user_id,app_id):
    '''
    Return the token of a specific user for a specific application. A User can have only one token per application. So if there are two applications,
    a user can have two tokens in the whole system. The function returns the user's token for a given application

    @input user_id : id of the user whose token we want
    @input app_id id of the application the token is associated with
    @output a dicitionary of token and expires keys. If no token is found, both key's have None as a value
    '''
    reply={'token':None,'expires':''}


    try:
        token_info=AccessToken.objects.get(user_id=user_id,application_id=app_id)

        token=token_info.token
        expireon=token_info.expires

        #if expired, delete existing tokens.
        dttime=datetime.now(settings.PYTZ_CONST)

        if expireon>=dttime:
            reply['token']=token
            reply['expires']=expireon

    except:
        #doesnt exist
        reply={'token':None,'expires':''}

    return reply




def generateUserApplicationToken(user_id, application_id, email, kind='a'):
    '''
    Generate a login token for a given user and a given a application. A User can have only one token per application. So if there are two applications,
    a user can have two tokens in the whole system. The function generates a token for the user for a specific application

    @input user_id : id of the user
    @input application_id id of the application token will be attached with
    @input email email of the user, used to generate the token
    @input kind a for access token, r for refresh token

    @output string token


    '''
    expire_seconds = settings.OAUTH2_PROVIDER.get(
        'ACCESS_TOKEN_EXPIRE_SECONDS', 86400)  # in seconds, what is the lifespan of the token?
    # add expire_second to today to create the exact expiration period
    expires = datetime.now(settings.PYTZ_CONST) + \
        timedelta(seconds=expire_seconds)
    exp = timegm(expires.timetuple())
    datetime.now(settings.PYTZ_CONST)

    salt = uuid.uuid4().hex  # generate a salt to be used when generating the token
    
    salt = hashlib.sha256(salt.encode()
                          ).hexdigest()  # hash the salt further

    # create the payload for jwt.encode()
    

    payload = {
        #'iat': int(time.time()),
        'id': user_id,
        'exp': exp,
        'app_id': application_id,
        'k': kind,
        's': salt
    }

    jwt_token = {'token': jwt.encode(
        payload, settings.JWT_AUTH['JWT_SECRET_KEY'])}

    

    token = jwt_token['token'].decode('utf-8')

    return token

def deleteUserApplicationToken(user_id,application_id=0):
    '''
    Delete a token of the given user. A User can have only one token per application. So if there are two applications,
    a user can have two tokens in the whole system.
    @input user_id the id of hte user whose token we want to revoke
    @input application_id is the application id the token is associationed with. If it is not 0, the token of the user associated with the specific application is deleted. Else, all tokens of the user will be deleted
    '''
    fields={'user_id':user_id}
    if application_id>0:
        fields['application_id']=application_id

    tokens=AccessToken.objects.filter(**fields)
    tokens.delete()
    refreshtokens=RefreshToken.objects.filter(**fields)
    refreshtokens.delete()


