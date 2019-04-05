
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from members.models import User, Task
from django.core.exceptions import ValidationError

from validation.validators import validateCharacters



class TaskSerializer(serializers.Serializer):
    '''
    Task serializer
    '''
    name = serializers.CharField(max_length=150,allow_blank=False,required=True)

    def validate(self,data):
        '''
        @input data: a dictionary that matches the serializer containing field names and values (i.e. name='Learn Python')

       '''

        errmsg={} #Since raise forms.ValidationError causes immediate termination

        valid_characters='' #used when checking if invalid characters/letters are used




        name=data.get('name','').strip()
        if len(str(name))<3 or len(str(name))>25:
            errmsg['first_name']=_('errorTaskName')
        else:
            valid_characters=validateCharacters(name,_('task_name'))
            if valid_characters:
                errmsg['name']=valid_characters

        if errmsg:
            raise serializers.ValidationError(errmsg)

        return data       
    

class UserSerializer(serializers.Serializer):
    '''
    New Member Registration serializer.
    @input display_name : String. Required. Not unique
    @input first_name : String. Required. Not unique
    @input last_name : String. Required. Not unique
    @input email : String. Required. Unique.
    @input password: Characters. Required
    @input confirm_password: Characters. Required
    @input lang: String. Valid language

    '''
    display_name=serializers.CharField(max_length=150,allow_blank=False,required=True)
    first_name=serializers.CharField(max_length=25,allow_blank=False,required=True)
    last_name=serializers.CharField(max_length=25,required=True,allow_blank=False)
    email=serializers.EmailField(required=True)
    password=serializers.CharField(max_length=16,allow_blank=False,required=True)
    confirm_password=serializers.CharField(max_length=16,allow_blank=False,required=True)
    lang=serializers.CharField(default=None,required=False)



    def __init__(self,*args,**kwargs):
        self.user_id=kwargs.pop('user_id')
        super(UserSerializer, self).__init__(*args, **kwargs)


    def validate(self,data):
        '''
        Validate member information is correct, during registration of a new member or updating information

        @input data: a dictionary that matches the serializer containing field names and values (i.e. first_name='Samuel')

       '''

        errmsg={} #Since raise forms.ValidationError causes immediate termination

        valid_characters='' #used when checking if invalid characters/letters are used

        if self.user_id==0:
            #required to provider display name since it is registration of a new user
            display_name=data.get('dispaly_name','').strip()
            check_display_name=displayNameIsValid(display_name)
            if check_display_name:
                errmsg['display_name']=check_display_name


        first_name=data.get('first_name','').strip()
        if len(str(first_name))<3 or len(str(first_name))>25:
            errmsg['first_name']=_('errorFirstName')
        else:
            valid_characters=validateCharacters(first_name,_('first_name'))
            if valid_characters:
                errmsg['first_name']=valid_characters



        last_name=data.get('last_name','').strip()
        if len(str(last_name))<3 or len(str(last_name))>25:
            errmsg['last_name']=(_('errorLastName'))
        else:
            valid_characters=validateCharacters(last_name,_('last_name'))
            if valid_characters:
                errmsg['last_name']=valid_characters

        email=data.get('email','')
        email_is_valid=userEmailIsValid(email,self.user_id) #returns a string
        if email_is_valid:
            errmsg['email']=email_is_valid


        password=data.get('password','')

        pwd_confirm=data.get('confirm_password','')

        pwd_check=passwordIsValid(pwd=password,pwd_confirm=pwd_confirm,compare_pwd=True)

        if pwd_check:
            errmsg['password']=pwd_check


        
        lang = data.get('lang','')
        if not languageIsValid(lang):
            errmsg['lang'] = _('errorInvalidLanguage')



        if errmsg:
            raise serializers.ValidationError(errmsg)

        return data



class ResetPasswordSerializer(serializers.Serializer):
    '''
    Reset my password serializer
    '''
    password=serializers.CharField(max_length=16)
    password_again=serializers.CharField(max_length=32)


    def validate(self,data):


        new_pwd_ok=passwordIsValid(data['password'],data['password_again'])
        if new_pwd_ok:
            raise serializers.ValidationError(new_pwd_ok)

        return data



class ChangePwdSerializer(serializers.Serializer):
    '''
    Change Password Serializer here
    '''
    password_current=serializers.CharField(max_length=70,allow_blank=False,required=True)
    password=serializers.CharField(max_length=16,allow_blank=False,required=True)
    password_new=serializers.CharField(max_length=16,allow_blank=False,required=True)


    def __init__(self,*args,**kwargs):
        self.user=kwargs.pop('user')
        super(ChangePwdSerializer, self).__init__(*args, **kwargs)


    def validate(self,data):
        pwd=data['password']
        pwd_current=data['password_current']
        pwd_new=data['password_new']
        errmsg={}

        if not pwd_current:
            errmsg['password_current']=(_('errorSecurityCurrentPwdEmpty'))

        else:
            if not self.user.passwordIsValid(pwd_current):
                errmsg['password_current']=(_('errorSecurityCurrentPwdBad'))


        if not pwd:
            errmsg['password']=(_('errorSecurityNewPwdEmpty'))
        else:
            pwd_check=passwordIsValid(pwd=pwd,pwd_confirm=pwd_new,compare_pwd=True)


            if pwd_check:
                errmsg['password']=(_(pwd_check))





        if errmsg:
            raise serializers.ValidationError(errmsg)

        return data


class ChangeEmailSerializer(serializers.Serializer):
    '''
    Change email of user
    '''
    password_current=serializers.CharField(max_length=70,allow_blank=False,required=True)
    new_email=serializers.CharField(max_length=30,required=True,allow_blank=False)

    def __init__(self,*args,**kwargs):
        self.user=kwargs.pop('user')
        super(ChangeEmailSerializer, self).__init__(*args, **kwargs)



    def validate(self,data):
        email=data['new_email']
        pwd_current=data['password_current']

        errmsg={}
        if not pwd_current:
            errmsg['password_current']=(_('errorSecurityCurrentPwdEmpty'))
        else:
            if not self.user.passwordIsValid(pwd_current):
                errmsg['password_current']=(_('errorSecurityCurrentPwdBad'))

        check_email=userEmailIsValid(email,user.id)
        if check_email:
            errmsg['new_email']=check_email



        if errmsg:
            raise serializers.ValidationError(errmsg)

        return data


