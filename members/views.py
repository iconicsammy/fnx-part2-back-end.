'''
 * Fenix International Challenge 2
 *
 * User Tasks Application
 *
 '''

from common_imports import *
from members.models import Task
from oauth2_provider.models import AccessToken, Application, RefreshToken
from django.contrib.auth import authenticate
from members.serializers import TaskSerializer
from tools.permissions import havePermission, userPermissions
from tools.tokens import deleteUserApplicationToken, generateUserApplicationToken,returnMyToken

class createNewTask(APIView):
    '''
    Create a new task. User must be logged in and have
    the permission to create tasks
    '''
    permission_classes = [TokenHasReadWriteScope]

    def post(self, request, format=None):
        '''
        accept data and create the task. But does the currently
        logged in user have the permission in the first place?
        '''
        reply = {}
        status = 400
        if havePermission(request.user.id, ['add_task']):
            #user is allowed to create tasks
            data = request.data
            serializer = TaskSerializer(data=data)

            if serializer.is_valid():
                content = serializer.validated_data

                task = Task(created_by = request.user, name = content['name'])
                task.save()
                # was the task added successfully?
                if task:
                    status = 200
                    reply['task_id'] = task.id
                    reply['message'] = _('newTaskAddedSuccessfully')            

        else:
            #no permission
            reply['message'] = _('noRight')
        
        return JsonResponse(reply,status=status)

class deleteTask(APIView):
    '''
    Delete a task. The user must have the permission to delete a task
    and be loggedin
    '''
    permission_classes = [TokenHasReadWriteScope]

    def delete(self, request, task_id, format=None):
        '''
        accept id of the task to delete.
        '''
        reply = {}
        status = 400
        if havePermission(request.user.id, ['delete_task']):
            #user is allowed to create tasks
            
            # try to delete it now
            try:
                task = Task.objects.get(pk=task_id)
                task.delete()
                status = 200
                reply['message'] = _('taskDeleted')
            except:
                reply['message'] = _('taskDeletionFailed')         

        else:
            #no permission
            reply['message'] = _('noRight')
        
        return JsonResponse(reply,status=status)

class editTask(APIView):
    '''
    Edit a task. The user must have the permission to edit a task
    and be loggedin
    '''
    permission_classes = [TokenHasReadWriteScope]

    def put(self, request, format=None):
        '''
        accept the id of the task to edit
        '''
        reply = {}
        status = 400
        if havePermission(request.user.id, ['change_task']):
            
            #user is allowed to create tasks
            data = request.data
            task_id = data.get('task_id', 0)
            # try to edit it now

            try:
            
                task = Task.objects.get(pk=task_id)
                
                serializer = TaskSerializer(data=data)

                if serializer.is_valid():
                    content = serializer.validated_data
                    task.name = content['name']
                    task.save()

                    status =200
                    reply['message'] = _('taskUpdated')

            except:
                reply['message'] = _('taskDeletionFailed')  

        else:
            #no permission
            reply['message'] = _('noRight')
        
        return JsonResponse(reply,status=status)


class tasks(APIView):
    '''
    View list of tasks we have. User needs to be logged in but needs no specific
    permission. We are not getting tasks of the user here alone. We are getting all
    tasks
    '''
    permission_classes = [TokenHasReadWriteScope]

    def get(self, request, format=None):
        '''
        '''
        reply = {}
        status = 200

        reply['tasks'] = list(Task.objects.all().values('name', 'id'))
        
        return JsonResponse(reply,status=status)


class taskView(APIView):
    '''
    View a specific task.
    Two way of giving it permission: user who created can read it or people with permission to
    view details of a task. We are going with permission here
    '''
    permission_classes = [TokenHasReadWriteScope]

    def get(self, request, task_id , format=None):
        '''
        '''
        reply = {}
        status = 400

        if havePermission(request.user.id, ['extra_can_read_task']):
            try:
                task = list(Task.objects.values('name').get(pk = task_id))
                status =200
                reply['task'] = task
            except:
                reply['message'] = _('taskNotFound')

        else:
            reply['message'] =_('noRight')

        return JsonResponse(reply,status=status)

class Login(APIView):
    '''
    Users login.

    A user can have maximum one token per application. So, if we have web and mobile
    application, a user can have unique token for each but only one per application

    Method: POST

    @input client_id : client id of the application
    @input client_secret: client secret of the application
    @input email: email of the user
    @input password: password of the user

    @output: status 400 if the login is unsuccessful with reason in detail key in response.
            status 200 if successful with keys:
                lang = language of the user
                detail = an object containing acess_token, first_name, display_name, expires
                permissions = an array of permissions of the user in the system
    '''

    permission_classes = []


    def post(self,request,format=None):

        print(request.data)

        client_id = request.data.get('client_id', '')
        client_secret = request.data.get('client_secret', '')
        email = request.data.get('email', '')
        pwd = request.data.get('password', '')


        reply = {}
        status = 400



        try:

            if client_id and client_secret:

                application = Application.objects.get(client_id = client_id,
                client_secret = client_secret,
                authorization_grant_type = 'password')



                user = authenticate(email=email, password=pwd)

                


                if user is not None:


                    lang = user.lang
                    

                    continue_token = False # should we continue generating token for the user?



                    if user.status == 0:
                        reply['detail']  = _('userBlocked')
                    elif user.status == 2:
                        reply['detail'] = _('userMissing')
                    elif user.status == 3:
                        reply['detail'] = _('userUnverified')
                    elif user.status == 1:
                        # user is allowed access
                        continue_token = True

                    
                    if not continue_token:
                        # delete possible tokens of the user cos user is not permitted
                        deleteUserApplicationToken(user.id)

                    else:
                        current_token = returnMyToken(user.id , application.id)

                        access_token_g = ''

                        if current_token['token'] is None:
                            # not existing. so create a new token
                            deleteUserApplicationToken(user.id , application.id) #any reminaning assurance clean up

                            expire_seconds = settings.OAUTH2_PROVIDER.get('ACCESS_TOKEN_EXPIRE_SECONDS', 86400)
                            expires = datetime.now() + timedelta(seconds = expire_seconds)

                            scopes = "" # the power of the token? what can it do in the system?

                            for scope in settings.OAUTH2_PROVIDER.get('SCOPES'):
                                scopes = ' '.join([scopes, scope])

                            # create access and refresh token now for the application

                            access_token = AccessToken.objects.create(
                            user=user,

                            application=application,
                            token=generateUserApplicationToken(user.id, application.id, user.email),
                            expires=expires,
                            scope=scopes)

                            RefreshToken.objects.create(
                            user=user,
                            token=generateUserApplicationToken(user.id, application.id, user.email, kind='r'),
                            access_token=access_token,
                            application=application)

                            access_token_g=access_token.token


                        else:
                            # user has a valid token for the application already

                            access_token_g = current_token['token']
                            expires = current_token['expires']



                        reply['lang'] = lang


                        reply['detail'] = {
                        'access_token': access_token_g,
                        'expires': expires,
                        'first_name': user.first_name,
                        'display_name': user.display_name
                        }

                        # send permissions now so front-end can build the UI
                        reply['rights']  =  userPermissions(user.id)
                        


                        status = 200



                else:

                    reply['detail'] = _('errorBadLoginDetails')

            else:

                reply['detail'] = _('errorBadLoginDetails')

        
        except:
            status = 400
            reply['detail'] = _('NoRight')
        
        

        return JsonResponse(reply,status=status)

