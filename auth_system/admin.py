from django.contrib import admin
from constance.admin import ConfigAdmin
from api.models import RefreshToken, User

admin.site.register(RefreshToken)
admin.site.register(User)
