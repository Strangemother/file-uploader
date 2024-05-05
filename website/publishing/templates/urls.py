
from trim import urls as shorts, names
from trim.models import grab_models

from . import views
from . import models
# from trim.urls import path_include, path_includes, error_handlers

app_name = 'history'

urlpatterns = shorts.paths_named(views,
    list=('PathAccessListView', ('', 'list/'),),
)
