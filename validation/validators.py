
from django.utils.translation import ugettext_lazy as _
from app.conf import base as settings
import re
from django.core.exceptions import ValidationError
import re
from members.models import User
from django.core.validators import validate_email
from constants.constants import INVALID_CHARACTERS, INVALID_CHARS_REPLACE_WITH


def passwordIsValid(pwd,pwd_confirm=None,compare_pwd=False):
    '''
    Check if password is accepted

    @input pwd: the password to check
    @input confirm: default None. If provided, it is expected to be the same as pwd so we are confirming the pwd (ie. confirm password field)

    @output string. Empty if no error, else the error message
    '''
    errmsg=''
    if len(str(pwd))<6 or len(str(pwd))>16:
        errmsg=_('errorSecurityPwdLength')
    else:
        if compare_pwd:
            if pwd_confirm is not None:
                if pwd_confirm!=pwd:
                    errmsg=_('errorSecurityPwdMismatch')
        else:
            errmsg=_('errorSecurityPwdMismatch')


    return errmsg



def emailIsValidFormat(email,required=True):
    '''
    Is the given email address valid format?

    @input email: email to be checked
    @input required: boolean, default True. If email is not required, set to False in which case empty emails will return still True.

    @output boolean. If required==True and email is not valid format, it returns False. If required==False, email is invalid format, email format is not checked so returns True
    '''

    if not email and not required:
        return True

    try:
        validate_email(email)
        return True
    except:
        return False





def userEmailIsValid(email,user_id):
    '''
    Make sure the user email is valid. Valid is:

    valid format
    unique in the system

    @input email: email to be checked
    '''

    try:
        validate_email(email)
        #format is valid. is it unique:
        excludes={}
        if user_id>0:
            excludes['pk']=user_id

        if User.objects.filter(email=email).exclude(**excludes).exists():
            return _('emailNotUnique')
    except:
        #format of email is in valid in the first place
        return _('errorInvalidEmail')

    return ''



def displayNameIsValid(value):
    '''
    Display name must contain only characters, numbers and underscore
    '''
    reply=''

    if re.match("^[A-Za-z0-9_]{6,18}$", value):
        reply=_('errorDisplayNameInvalid')

    return reply


def validateCharacters(value, field_name, replace_them=False):
    '''
    We have a predefined list of character names that are not valid in constants
    On top, we must always make sure there is no | in the value to be validated.
    if replace with is True, then dont replace. Instead return back the error. Error replace the badcharacters and move on
    '''
    errmsg = ''
    
    invalid_chars = INVALID_CHARACTERS


    if "|" not in invalid_chars:
        invalid_chars=''.join([invalid_chars,"|"])

    #check if value contains any of the invalid characters now
    if replace_them:
        invalid_chars='[' + invalid_chars + ']'
        new_value = re.sub(invalid_chars, INVALID_CHARS_REPLACE_WITH, value)
        return new_value

    #give error message instead
    #create a list of the invalid characters first

    invalid_chars_l=[]
    for c in invalid_chars:
        invalid_chars_l.append(c)


    if any(x in value for x in invalid_chars_l):
        errmsg=_('errorContainsInvalidCharacters') % {'field_name':field_name,'chars':invalid_chars}


    return errmsg

