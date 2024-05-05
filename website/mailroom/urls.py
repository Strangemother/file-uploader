
from trim import urls as shorts, names
from trim.models import grab_models

from . import views
from . import models
# from trim.urls import path_include, path_includes, error_handlers

app_name = 'mailroom'

urlpatterns = shorts.paths_named(views,
    # submit=('BasketAddFormView','submit/'),
    sent=('UserEmailSentListview', 'sent/',),
    form=('EmailFormView', 'form/',),
    templates=('EmailTemplateListView', 'templates/',),
    template=('EmailTemplateDetailView', 'templates/<str:pk>/',),
    # save=('SaveBasketForLater','save/'),
    # add_success=('BasketAddSuccessView','success/'),
    # save_success=('BasketSaveForLaterSuccessView','success/'),
    # user=('UserBasketListView',''),
    # create=('CreateView','new/'),
    # update=('UpdateView','change/<str:pk>/'),
    # delete=('DeleteView','delete/<str:pk>/'),
    # detail=('DetailView','<str:pk>/'),
)
