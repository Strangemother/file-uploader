from django.shortcuts import render
from trim import views


class ExplorerView(views.TemplateView):
    """A Visual display for files (A JS Explorer).
    """
    template_name = 'explorer/explorer_view.html'
