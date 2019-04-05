from django.conf.urls import url

from members import views
urlpatterns = [

    url(r'^new-task/$', views.createNewTask.as_view(), name='new-task'),
    url(r'^view-tasks/$', views.tasks.as_view(), name='view-tasks'),
    url(r'^delete-task/(?P<task_id>[0-9]+)/$', views.deleteTask.as_view(), name='delete-task'),
    url(r'^edit-task/$', views.editTask.as_view(), name='edit-task'),
    url(r'^view-task/(?P<task_id>[0-9]+)/$', views.taskView.as_view(), name='view-task'),
    url(r'^login/$', views.Login.as_view(), name='login'),


]
