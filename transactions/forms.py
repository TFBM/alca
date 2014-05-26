#-*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button

#Constants
BTC_MAX_DIGIT = 16
BTC_DECIMAL = 8

class newTransactionForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(newTransactionForm, self).__init__(*args)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'new'

        self.helper.add_input(Submit('submit', 'Send'))
        if "pubKey" in kwargs: 
            self.fields["pubKey"].choices = [(pk.value, "%s (%s)" % (pk.name, pk.value)) for pk in kwargs['pubKey']]
        
    good = forms.CharField(label="Good Name", max_length=255, widget=forms.TextInput())
    description = forms.CharField(label="Description of the good", max_length=2500, widget=forms.Textarea())
    price = forms.DecimalField(label="Price asking (BTC)", max_digits=BTC_MAX_DIGIT,decimal_places=BTC_DECIMAL, widget=forms.TextInput())
    buyer_email = forms.CharField(label="Email buyer", max_length=255, widget=forms.TextInput())
    pubKey = forms.ChoiceField(label="Public Key", widget=forms.Select())
