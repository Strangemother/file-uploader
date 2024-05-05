from django.shortcuts import render
from trim import views

from pathlib import Path
from django.contrib.auth import get_user

from . import forms, models


class ContentPublishListView(views.ListView):
    model = models.ContentPublish

    def get_queryset(self):
        qs = super().get_queryset()
        u = get_user(self.request)
        if u.is_anonymous:
            return qs.filter(is_public=True)
        return qs.filter(user__pk=u.id)


class PublishContentFormView(views.FormView):
    form_class = forms.PublishContentForm
    template_name = 'publishing/form.html'
    model = None

    def form_valid(self, form):
        data = form.cleaned_data
        public = data['is_public']
        path = Path(self.kwargs.get('path'))
        ms = models.ContentPublish.objects.filter(
                    user__pk=self.request.user.pk,
                    fullpath=path.as_posix(),
                )

        if ms.exists():
            cp = ms.latest('created')
            cp.is_public = public
            cp.save()
        else:
            cp = models.ContentPublish.objects.create(
                    user=self.request.user,
                    fullpath=path.as_posix(),
                    is_public=public,
                )
        self.model = cp
        return super().form_valid(form)



    def get_success_url(self):
        args = ()
        if self.model:
            args = (self.model.uuid, )
        return views.reverse('publishing:publish_success', args=args)


class PublishContentSuccessView(views.TemplateView):
    template_name = 'publishing/published.html'