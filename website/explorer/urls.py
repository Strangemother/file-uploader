from trim import urls
from . import views

app_name = 'explorer'

urlpatterns = urls.paths_named(views,
    explorer=('ExplorerView',
            ('', '<path:path>')
        ),
)