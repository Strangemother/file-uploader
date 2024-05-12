from trim import urls
from . import views

app_name = 'box'

urlpatterns = urls.paths_named(views,
    list=('BoxListView', ''),
    create=('BoxSimpleCreateView', 'create/',),
    link_form=('BoxContentLinkFormView', (
                                'add/<uuid:uuid>/',
                                'add/<uuid:uuid>/<path:path>',
            ),
        ),
    # edit=('PathTagUpdateFormView', 'edit/<slug:slug>/',),
    detail=('BoxDetailView', 'detail/<uuid:uuid>/',),
)