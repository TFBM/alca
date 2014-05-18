#-*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button

class EditUsernameForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(EditUsernameForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'edit'

        self.helper.add_input(Submit('submit', 'Change'))
        self.helper.add_input(Button('', "Cancel", css_class='btn btn-danger', css_id='username-cancel'))

    username = forms.CharField(label="", max_length=30, widget=forms.TextInput())
