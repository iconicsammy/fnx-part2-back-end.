from django.urls import reverse
from oauth2_provider.models import Application, AccessToken
from rest_framework.test import APITestCase
from members.models import User, Task
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
from django.contrib.auth.models import Permission

class TasksTest(APITestCase):
    """ Tasks test """

    def setUp(self):
        '''
        Create user first
        '''
        self.task_adding_user=User.objects.create_user(password=1234,first_name='User 1',last_name='User 1',is_superuser=0,display_name='User1',email='user1@testy.test',is_staff=0,status=3,lang='en')
        self.task_adding_user.save()

        self.task_editing_user=User.objects.create_user(password=1234,first_name='User 2',last_name='User 2',is_superuser=0,display_name='User2',email='user2@testy.test',is_staff=0,status=3,lang='en')
        self.task_editing_user.save()

        self.task_deleting_user=User.objects.create_user(password=1234,first_name='User 3',last_name='User 3',is_superuser=0,display_name='User3',email='user3@testy.test',is_staff=0,status=3,lang='en')
        self.task_deleting_user.save()

        #system admin user
        admin_user_data = {'first_name': 'Admin', 'last_name':'System','email': 'admin@testy.com','password' : 'kigali11', 'status': 1, 'is_superuser':1, 'is_staff':1, 'display_name':'Admin'}

        self.admin_user = User.objects.create_user(**admin_user_data)
        app = {'name': 'web application', 'client_id': 'client_id', 'client_secret': 'secret', 'authorization_grant_type' : 'password', 'user_id': self.admin_user.id}
        self.app = Application(**app)
        self.app.save()

        self.new_task_url = reverse('new-task')
        self.edit_task_url= reverse('edit-task')
        self.view_tasks_url= reverse('view-tasks')
    

    

    def test_create_task(self):
        '''
        Create new task
        User is not logged in so get 401
        '''
        payload = {'name' : 'Test Task'}
        response = self.client.post(self.new_task_url , payload, format='json')
        self.assertEqual(response.status_code, 401)

        #login the user now
        access_token = AccessToken.objects.create(
        user=self.task_adding_user,

        application=self.app,
        token=self.task_adding_user.id,
        expires=datetime.now() + timedelta(seconds = 90000),
        scope='groups read write')
        
        access_token.save()
        #user is logged in but no permission. we should get 400
        header = {'Authorization': 'Bearer ' + str(self.task_adding_user.id)}
        response = self.client.post(self.new_task_url , data = payload, **header)
        self.assertEqual(response.status_code, 400)

        #give user the permission
        permission = Permission.objects.get(codename='add_task')
        self.task_adding_user.user_permissions.add(permission)
        # add now
        response = self.client.post(self.new_task_url , data = payload, **header)
        self.assertEqual(response.status_code, 200)        

    def test_delete_task(self):
        '''
        Delete task

        '''
        task_id = 1
        payload = {'task_id' : 1}
        response = self.client.delete(reverse('delete-task', args=(task_id,)) )
        self.assertEqual(response.status_code, 401)

        #login the user now
        access_token = AccessToken.objects.create(
        user=self.task_deleting_user,
        application=self.app,
        token=self.task_deleting_user.id,
        expires=datetime.now() + timedelta(seconds = 90000),
        scope='groups read write')
        access_token.save()

        #user is logged in but no permission. we should get 400
        header = {'Authorization': 'Bearer ' + str(self.task_deleting_user.id)}

        response = self.client.delete(reverse('delete-task', args=(task_id,)) , **header)
        self.assertEqual(response.status_code, 400)

        #give user the permission: create add and delet permissions
        permission = Permission.objects.get(codename='delete_task')
        self.task_deleting_user.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_task')
        self.task_deleting_user.user_permissions.add(permission)

        # try deleting non existing task
        response = self.client.delete(reverse('delete-task', args=(task_id,)) , **header)
        self.assertEqual(response.status_code, 400)
        #add the task now        
        response = self.client.post(self.new_task_url , data = {'name': 'Task'}, **header)
        #now delete
        response = self.client.delete(reverse('delete-task', args=(task_id,)) , **header)
        self.assertEqual(response.status_code, 200)   

    
    def test_edit_task(self):
        '''
        Edit task

        '''
        payload = {'task_id' : 1}
        response = self.client.put(self.edit_task_url, payload)
        self.assertEqual(response.status_code, 401)

        #login the user now
        access_token = AccessToken.objects.create(
        user=self.task_editing_user,
        application=self.app,
        token=self.task_editing_user.id,
        expires=datetime.now() + timedelta(seconds = 90000),
        scope='groups read write')
        access_token.save()

        #user is logged in but no permission. we should get 400
        header = {'Authorization': 'Bearer ' + str(self.task_editing_user.id)}

        response = self.client.put(self.edit_task_url, payload, **header)
        self.assertEqual(response.status_code, 400)

        #give user the permission: create add and edit permissions
        permission = Permission.objects.get(codename='change_task')
        self.task_editing_user.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_task')
        self.task_editing_user.user_permissions.add(permission)
        
        # try edit non existing task
        response = self.client.put(self.edit_task_url, payload, **header)
        self.assertEqual(response.status_code, 400)
        
        #add the task now        
        response = self.client.post(self.new_task_url , data = {'name': 'Task'}, **header)
        
        #now edit
        payload['name'] = 'New Task Name'

        response = self.client.put(self.edit_task_url, payload, **header)
        self.assertEqual(response.status_code, 200)
        
    def test_list_tasks(self):
        '''
        List all tasks. We don't need permission to view except to being logged in.

        '''

        payload = {'name' : 'Task Name'}

        response = self.client.get(self.view_tasks_url)
        self.assertEqual(response.status_code, 401)

        #login the user now
        token = {
        'user':self.task_adding_user,
        'application':self.app,
        'token':self.task_adding_user.id,
        'expires':datetime.now() + timedelta(seconds = 90000),
        'scope':'groups read write'
        }
        access_token = AccessToken.objects.create(**token)
        access_token.save()     
 
        #user is logged in but no permission. we should get 400
        header = {'Authorization': 'Bearer ' + str(self.task_adding_user.id)}

        #give user the permission
        permission = Permission.objects.get(codename='add_task')
        self.task_adding_user.user_permissions.add(permission)
        # add now
        response = self.client.post(self.new_task_url , data = payload, **header)
        self.assertEqual(response.status_code, 200)

        #any logged in user should see now tho   
        #login second user
        token['user'] = self.task_editing_user
        token['token'] = self.task_editing_user.id
        access_token = AccessToken.objects.create(**token)
        access_token.save()
        header = {'Authorization': 'Bearer ' + str(self.task_editing_user.id)}

        response = self.client.get(self.view_tasks_url, **header)
        self.assertEqual(response.status_code, 200)

    def test_view_task(self):
        '''
        View a specific task

        '''

        payload = {'name' : 'Task Name'}

        task_id = 1

        response = self.client.get(reverse('view-task', args=(task_id,)) )
        self.assertEqual(response.status_code, 401)

        #login the user now
        token = {
        'user':self.task_adding_user,
        'application':self.app,
        'token':self.task_adding_user.id,
        'expires':datetime.now() + timedelta(seconds = 90000),
        'scope':'groups read write'
        }
        access_token = AccessToken.objects.create(**token)
        access_token.save()     
 
        #user is logged in but no permission. we should get 400
        header = {'Authorization': 'Bearer ' + str(self.task_adding_user.id)}

        #give user the permission
        permission = Permission.objects.get(codename='add_task')
        self.task_adding_user.user_permissions.add(permission)
        # add now
        response = self.client.post(self.new_task_url , data = payload, **header)
        self.assertEqual(response.status_code, 200)


        #any logged in user should see now tho   
        #login second user
        token['user'] = self.task_editing_user
        token['token'] = self.task_editing_user.id
        access_token = AccessToken.objects.create(**token)
        access_token.save()
        header = {'Authorization': 'Bearer ' + str(self.task_editing_user.id)}

        # try to see the post now with no permission
        response = self.client.get(reverse('view-task', args=(task_id,)) , **header)
        self.assertEqual(response.status_code, 400)
        #give the user permission
        permission = Permission.objects.get(codename='extra_can_read_task')
        self.task_editing_user.user_permissions.add(permission)

        response = self.client.get(reverse('view-task', args=(task_id,)) , **header)
        self.assertEqual(response.status_code, 200)
