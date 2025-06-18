from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User
from .models import Organization, Department, Program, Office, Position

admin.site.register(Organization)
admin.site.register(Department)
admin.site.register(Program)
admin.site.register(Office)
admin.site.register(Position)
