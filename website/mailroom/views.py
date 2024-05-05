from django.shortcuts import render
from trim import views, get_model
from post_office import models as po_models
from django.template import Context, Template

from . import forms


class UserEmailSentListview(views.ListView):
    """Return all the messages for the user
    """
    paginate_by = 50

    def get_queryset(self):
        M = get_model('post_office.Email')
        email = self.request.user.email
        return M.objects.filter(to=email).order_by('-created')


class EmailFormView(views.FormView):
    form_class = forms.EmailForm
    template_name = 'mailroom/email_form.html'


class EmailTemplateListView(views.IsStaffMixin, views.ListView):
    model = po_models.EmailTemplate


class EmailTemplateDetailView(views.IsStaffMixin, views.DetailView):
    model = po_models.EmailTemplate

    def render_email(self):
        template = self.get_object()
        context = self.get_context_data()

        return template.render_demo(context)


class EmailTemplateRenderDetailView(views.IsStaffMixin, views.DetailView):
    model = po_models.EmailTemplate

