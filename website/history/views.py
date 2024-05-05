from django.shortcuts import render

from trim import views
from . import models
# Create your views here.


class PathAccessListView(views.OrderPaginatedListView):
    """Present a list of history items.
    """
    default_orderby = '-created'
    model = models.PathAccess
    default_selected_orderby = 'created'
    default_direction = 'asc'
    ordering = f'{default_orderby}'

    min_paginate_by = 20
    max_paginate_by = 200
    paginate_by = 50

    ordering_fields = (
        # ext. val, ext. label, int. key
        ('created', ('Date', 'created')),
        ('fullpath', ('Name', 'fullpath',)),
    )

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.using('history').filter()#user__pk=get_user(self.request).id)

