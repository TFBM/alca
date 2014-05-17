from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class RegisterForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'register'

        self.helper.add_input(Submit('submit', 'Register'))

    username = forms.CharField(label="Username", max_length=30, widget=forms.TextInput())
    email = forms.CharField(label="Email", max_length=30, widget=forms.TextInput())
    password = forms.CharField(label="Enter Password", widget=forms.PasswordInput())
    password_bis = forms.CharField(label="Re-enter Password", widget=forms.PasswordInput())
    check = forms.BooleanField(required=True)
    


class AuthenticationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'login'

        self.helper.add_input(Submit('submit', 'Login'))
        
    username = forms.CharField(label="Username", max_length=30, widget=forms.TextInput())
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

