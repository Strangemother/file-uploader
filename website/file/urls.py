from trim import urls
from . import views

app_name = 'file'


urlpatterns = urls.paths_named(views,
    list=('UserFileUnitListView', ''),
    upload_chunk=('UploadChunkModelView', (
            'upload/chunk/',
            'upload/chunk/<str:extra>/',
            )
        ),

    upload=('UploadAssetModelCreateView', ('add/', 'file/', )),
    open=('FileOpenView', 'open/<path:path>'),
    merge=('MergeAssetModelView', 'upload/merge/<str:uuid>/'),
    upload_success=('UploadAssetSuccessModelView', 'upload/success/<str:uuid>/'),
    download=('DownloadAccessibleFileModelView', 'download/<str:uuid>/'),
    file_detail=('FileDetailView', 'detail/<str:uuid>/'),
    file_read=('AccessFileView', 'read/<path:path>'),
)