"""Register your models here for Admin Dashboard."""
from django.contrib import admin

from users.models import BaseUser

# Register your models here.
admin.site.register(BaseUser)
