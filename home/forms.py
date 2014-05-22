#-*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button

#Constants

BTC_MAX_DIGIT = 16
BTC_DECIMAL = 8

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

class newTransactionForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(newTransactionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'new'

        self.helper.add_input(Submit('submit', 'Send'))

    good = forms.CharField(label="Good Name", max_length=255, widget=forms.TextInput())
    description = forms.CharField(label="Description of the good", widget=forms.Textarea())
    price = forms.DecimalField(label="Price asking", max_digits=BTC_MAX_DIGIT,decimal_places=BTC_DECIMAL, widget=forms.TextInput())
    buyer_email = forms.CharField(label="Email buyer", max_length=255, widget=forms.TextInput())

