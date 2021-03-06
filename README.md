# Fenix Intl Part 2 Challenge Back End

The application runs on python 3

Create virtual envrionment and install requirements via pip install -r requirements.txt

# Using Django Rest Framework

There are several reasons I chose to implement the solution via DRF with the main ones being:

    - Application management: with drf, it is easy to have as many appilications as necessary and tweak the experience based on the application connected. For .e.g if we were to serve list of tasks to web app and ussd, the data to serve would have to be different. We can define two applications and based on the source of the request coming, alternate the output.

    - Amazing built-in JSON Support: makes API development for different devices (web, ussd and mobile apps) quite easy, thus making scaling up quite easy

    - Separate server and client entities, which makes debugging and working easier and manageable since failure of one entity is isolated from the rest.

    - The stateless calls of APIs and how they can be called indepedently of each other enables growth and testing easier.

    - DRF built-in cache mechanisim is quite efficient by design and where necessary, can be enhanced by the use of libraries such as reddis

    - I simply love doing in python and from the python web frameworks, I like Django the most.



# Running the app

python manage.py runserver localhost:9011

the front-end is configured to talk to the backend on port 9011. So if you want to run the backend on a different port, please configure front-end environment files.

# API Doc

    localhost:9011/docs

# Adding Users

open localhost:9011/admin/

    email : admin@fnx.net
    password : fenixintl11

Add users as much as you like

# Permissions

There are built in permissions for the system but there are four permissions we want to work with

    add_task
    change_task
    delete_task
    extra_can_read_task

A user can have any number of permissions.

# End User Testing

With both backend and front end running and users created, you should login via the front-end and check permissions are working. For e.g. if a user doesn't have add_task permission, he/she won't be able to add
tasks to the system

# Automated testing

    python manage.py test

# Permission Management

Permission is handled on two levels: login status of the user and permissions. A user could be logged in to the system but might not have a permission to a specific resource.

