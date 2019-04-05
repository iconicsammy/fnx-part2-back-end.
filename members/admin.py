from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from members.forms import UserAdminCreationForm, UserAdminChangeForm
from members.models import User


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('first_name', 'last_name', 'email',
                    'is_staff', 'lang', 'status')
    list_filter = ('is_staff', 'status')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('email', 'first_name',
                                      'last_name', 'lang', 'status')}),
        ('Permissions', {'fields': ('is_staff','groups', 'user_permissions')})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'lang', 'is_staff')}
         ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('first_name',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
