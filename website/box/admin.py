from django.contrib import admin
from trim import admin as t_admin

from . import models

t_admin.register_models(models)