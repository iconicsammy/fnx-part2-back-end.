from django.utils.translation import ugettext_lazy as _

INVALID_CHARACTERS = '/?'
INVALID_CHARS_REPLACE_WITH = ' '


USER_ACCOUNT_STATUS = [

    (1, _('working')),
    (0, _('blocked')),
    (2, _('deleted')),
    (3, _('unverified'))
]
