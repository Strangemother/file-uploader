from trim import urls
from . import views

app_name = 'drives'

urlpatterns = urls.paths_named(views,
    note_list=('ContentNoteListView', 'notes/'),

    list=('DriveListView', ''),
    detail=('DriveDetailView', '<str:name>/'),
    file=('FileDetailView', (
                            'file/<str:name>/<path:path>',
                            'file/<path:path>',
                            )
    ),
    content=('DriveContentListView', (
                    'drive/<str:name>/<path:path>',
                    'drive/<path:path>',
                    )
    ),
    json=('JSONDriveContentListView', (
                    'json/<str:name>/<path:path>',
                    'json/<path:path>',
                    )
    ),

    explorer=('DriveExplorerView', (
                    'drive/<str:name>/<path:path>',
                    'drive/<path:path>',
                    )
    ),
    # tag=('PathTagFormView', 'tag/<path:path>',)
)