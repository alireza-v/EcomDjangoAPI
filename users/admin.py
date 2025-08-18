from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

# unregister Django's default Group model
admin.site.unregister(Group)

# unregister SimpleJWT blacklist models
admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)
