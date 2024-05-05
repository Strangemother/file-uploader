from trim import urls
from . import views

app_name = 'tags'

urlpatterns = urls.paths_named(views,
    list=('PathTagListView', ''),
    form=('PathTagFormView', 'tag/<path:path>',),
    edit=('PathTagUpdateFormView', 'edit/<slug:slug>/',),
    detail=('PathTagDetailView', 'detail/<slug:slug>/',),
)