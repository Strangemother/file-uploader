import uuid
import os
from pathlib import Path

from django.shortcuts import render
from django.core.files.storage import default_storage, FileSystemStorage
from django.contrib.auth import get_user

import json

from trim.views.download import streamfile_response
from trim.merge import FileExists, recombine
from trim import views

from trim.views.upload import (
    UploadAssetSuccessView,
    unlink_dir_files,
    UploadChunkView,
    UploadAssetView,
    MergeAssetView,
    get_cache,
)

from . import models


HERE = Path(__file__).parent
ROOT = HERE.parent.parent
UPLOADS = ROOT / "uploads"

fs = FileSystemStorage(location=UPLOADS)


class FileDetailView(views.DetailView):
    template_name = "file/file_detail.html"
    model = models.FileUnit
    slug_url_kwarg = 'uuid'
    slug_field = 'file_uuid'


class UserFileUnitListView(views.ListView):
    model = models.FileUnit

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user__pk=get_user(self.request).id)


class UploadAssetSuccessModelView(UploadAssetSuccessView):
    template_name = 'file/upload_success.html'

    def get_asset(self):
        """return the DB model
        """
        file_uuid = self.kwargs['uuid']

        info = models.FileUnit.objects.filter(
                file_uuid=file_uuid,
            ).get()
        return info


    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['asset'] = self.get_asset()
        return kwargs


class MergeAssetModelView(MergeAssetView):

    def get_asset(self):
        """return the DB model
        """
        file_uuid = self.kwargs['uuid']

        info = models.FileUnit.objects.filter(
                file_uuid=file_uuid,
            ).get()
        return info


    def get_parts_dir(self):
        """Override to use the db model rather than the dict cache
        """
        file_uuid = self.get_uuid()
        info = self.get_asset()
        name = info.internal_name
        suffix = info.suffix
        username = self.get_current_username()
        make_name = Path(username) / file_uuid
        return make_name


    def perform_all(self, delete_cache=False):
        asset = self.get_asset()
        input_perform_asset = self.resolve_paths()
        # asset['input'] = input_perform_asset

        dir_path = input_perform_asset['path']

        out_path = self.get_out_dir()
        if dir_path.exists():
            output = self.perform(asset, dir_path, out_path)
            # asset['output'] = output
            if delete_cache:
                self.delete_cache(input_perform_asset, asset=asset)
            return True
            # return super().form_valid(form)
        return False

    def perform(self, asset, dir_path, out_path):
        try:
            output_path = recombine(dir_path, out_path)
        except FileExists as err:
            output_path = err.args[0]
            print('ERROR; File already exists', output_path)
        output_path = Path(output_path)
        fs = self.get_fs()

        result = {
            "path": output_path.relative_to(fs.location).as_posix(),
            "exists": output_path.exists(),
            "size": os.path.getsize(output_path),
            'sub_path': output_path.relative_to(out_path).as_posix(),
            'uuid': self.get_uuid(),
        }

        result['output_path'] = Path(result['path']).as_posix()
        result['done'] = True
        result['verification'] = self.verify_file(result, asset)

        asset.done = True
        asset.verification = result['verification']
        asset.store_path = output_path

        asset.save()

        return result

    def verify_file(self, result, asset):
        res = {
            'size': result['size'] == asset.bytesize
        }

        return res

    def delete_cache(self, input_perform_asset, asset):
        """Override to ensure the deleted record is applied to
        the DB model correctly.
        """
        # delete the merge parts.
        print('Delete')
        p = Path(input_perform_asset['path'])
        if p.exists() and p.is_dir():
            # scrub it
            print('Delete', p)
            deleted = unlink_dir_files(p)

            # asset['deletion'] = deleted
            receipt = p / 'delete-receipt.json'
            receipt.write_text(json.dumps(deleted, indent=4))

            asset.deletion = deleted
            asset.save()

        return p.exists() is False


class UploadChunkModelView(UploadChunkView):
    """Override the store chunk view to read the DB reference.
    """

    def generate_store_path(self, data):
        """Override to read the db info.
        Create a new associated record for the upload.

        Return an unchanged store-path
        """
        # returned from the upload asset initial view.
        file_uuid = data['file_uuid']

        info = models.FileUnit.objects.filter(
                file_uuid=file_uuid,
            ).get()

        username = self.get_current_username()
        # The mapped name given to the form before the main upload
        name = info.internal_name
        suffix = info.suffix

        # The int chunk index
        index = data['chunk_index']
        # The 'part' defines an extended suffix,
        # to flag this is a partial file.
        part = f".part_{index}"
        filename = f"{name}{suffix}{part}" # received file name
        make_name = Path(username) / file_uuid / filename
        # fs.location is enforced.
        store_path = self.ensure_fullpath(make_name)
        return store_path


class UploadAssetModelCreateView(UploadAssetView):
    template_name = 'upload/upload_view.html'

    def save_asset(self, data):
        fu = self.db_save_asset(data)
        return fu.file_uuid

    def db_save_asset(self, data):
        file_uuid = str(uuid.uuid4())
        filename = data['filename']
        if len(filename) == 0:
            filename = "foo.unknown"

        suffix = Path(data['filepath']).suffix
        name = Path(data['filename']).stem
        # get or create a model.
        fu_models = models.FileUnit.objects.filter(
                file_uuid=file_uuid,
            )
        fu_exists = fu_models.exists()

        if fu_exists:
            return fu_models.get()

        user = get_user(self.request)
        user_or_none = None if user.is_anonymous else user

        print('New model', name)
        mdata = {
            'name': name,
            'suffix': suffix,
            'file_uuid':file_uuid,
            'bytesize': data['byte_size'],
            'filepath': data['filepath'],
            'filetype': data['filetype'],
            'filename': filename,
            'internal_name': name,
            'done': False,
            'user': user_or_none,
        }

        fu = models.FileUnit.objects.create(**mdata)
        # for field, value in mdata.items():
        #     setattr(fu, field, value)
        # fu.save()
        return fu


class DownloadAccessibleFileView(views.TemplateView):
    template_name = "file/download_file.html"

    def get_current_username(self):
        username = self.request.user.username
        if len(username) == 0 and self.request.user.is_anonymous:
            username = 'anonymous'
        return username

    def resolve_fullpath(self, uuid):
        # username = self.get_current_username()
        path = get_cache()[uuid]['output']['path']
        # Resolve with the given path
        root = Path(fs.location)
        out_path = root / path
        sub_path = out_path.resolve().relative_to(root) # for asserting the root
        return out_path
        # return sub_path

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        path = self.resolve_fullpath(self.kwargs['uuid'])
        name = context.get('filename') or path.name
        return streamfile_response(path, name)
        # return self.render_to_response(context)


class DownloadAccessibleFileModelView(DownloadAccessibleFileView):

    def get_asset(self):
        """return the DB model
        """
        file_uuid = self.kwargs['uuid']

        info = models.FileUnit.objects.filter(
                file_uuid=file_uuid,
            ).get()
        return info

    def resolve_fullpath(self, uuid):
        # username = self.get_current_username()
        path = self.get_asset().store_path
        # Resolve with the given path
        root = Path(fs.location)
        out_path = root / path
        sub_path = out_path.resolve().relative_to(root) # for asserting the root
        return out_path
        # return sub_path
