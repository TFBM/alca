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

class EditEmailForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(EditEmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'edit'

        self.helper.add_input(Submit('submit', 'Change'))
        self.helper.add_input(Button('', "Cancel", css_class='btn btn-danger', css_id='email-cancel'))

    email = forms.CharField(label="", max_length=30, widget=forms.TextInput())

class EditBitmessageForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(EditBitmessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'edit'

        self.helper.add_input(Submit('submit', 'Change'))
        self.helper.add_input(Button('', "Cancel", css_class='btn btn-danger', css_id='bitmessage-cancel'))

    bitmessage = forms.CharField(label="", max_length=30, widget=forms.TextInput())

class EditPublicKForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(EditPublicKForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'edit'

        self.helper.add_input(Submit('submit', 'Change'))
        self.helper.add_input(Button('', "Cancel", css_class='btn btn-danger', css_id='publicK-cancel'))

    publicK = forms.CharField(label="", max_length=30, widget=forms.TextInput())
    
class AddPublicKForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(AddPublicKForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'add'

        self.helper.add_input(Submit('submit', 'Add'))
        self.helper.add_input(Button('', "Cancel", css_class='btn btn-danger', css_id='publicK-cancel'))

    value = forms.CharField(label="Public Key", max_length=130, widget=forms.TextInput())
    name = forms.CharField(label="Name of the public key", max_length=30, widget=forms.TextInput())
    comment = forms.CharField(label="Comment", widget=forms.Textarea())
    default = forms.BooleanField(label="Key is to be used by default", widget=forms.CheckboxInput())
