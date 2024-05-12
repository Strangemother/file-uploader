from pathlib import Path

from django.shortcuts import render
from trim import views

from django.conf import settings

from .reader.image import resize_file
from .reader.win_exe import extract_icon


class ResizeFileView(views.TemplateView):
    template_name = 'thumbnailer/resize-file.html'


    def get_object(self):
        path = self.kwargs.get('path')
        p = Path(path)
        if p.suffix == '.exe':
            return extract_icon(p)

        if p.exists():
            # new path
            return resize_file(p)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
