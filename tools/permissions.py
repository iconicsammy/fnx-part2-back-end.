
from members.models import User
from django.contrib.auth.models import Permission
from itertools import chain


def havePermission(user_id, needed_permissions=[]):
    '''
    Does the user have requested permission?

    @input user_id: the user id whose permission or rights for the given association needs to be checked
    @input needed_permissions: an array of permissions we need to check

    @output boolean. True if permitted. Else, False (default).

    Note: if needed_permissions contains more than one permissions, reply will be True
    if one of them is permitted.

    Note 2: the permission might be as part of a group or assigned individually
    '''
    reply = False

    group_permissions_exist = False

    if needed_permissions:
        try:
            user = User.objects.get(pk = user_id)
            groups = list(user.groups.all())

            group_permissions_exist = Permission.objects.filter(
                group__in=groups, codename__in=needed_permissions).exists()
        except:
            pass
        
        individual_permissions = Permission.objects.filter(user__id=user_id,codename__in=needed_permissions).exists()

        reply = group_permissions_exist or individual_permissions

    return reply


def userPermissions(user_id):
    '''
    Returns permissions of a user in the form of an array.
    The permissions could be through groups the user belongs
    or permissions assigned to the user individually

    @input user_id : id of the user whose permissions we want


    @output an array of permissions
    '''
    user_permissions = []
    group_permissions = []
    individual_permissions = []

    try:
        user = User.objects.get(pk=user_id)
        groups = list(user.groups.all())

        group_permissions = Permission.objects.filter(
            group__in=groups).values_list('codename', flat=True)


        individual_permissions = user.user_permissions.all().values_list('codename', flat=True)

        # chain them up now
        user_permissions = list(group_permissions) + list(individual_permissions)
        # clear possible duplicates since the UI might be confused
        user_permissions = list(set(chain(user_permissions)))
    
    except:
        print('here')
        user_permissions = []
    

    return user_permissions
