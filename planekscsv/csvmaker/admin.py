from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Schema)
admin.site.register(models.Column)
admin.site.register(models.Dataset)
