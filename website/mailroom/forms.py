from django import forms

from . import models
from post_office import models as pmodels


class EmailForm(forms.ModelForm):

    # basket_id = forms.CharField()
    # name = forms.CharField()

    class Meta:
        # fields = ('name',)
        # fields = '__all__'
        exclude = ('status',)
        model = pmodels.Email
