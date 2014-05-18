from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from manageuser.forms import AuthenticationForm, RegisterForm
from django.db import IntegrityError

def login_view(request):
    if request.user.is_authenticated():
        return redirect("profil")
        
    if request.method == 'POST':
        form = AuthenticationForm(request.POST) 

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("home")
                else:
                    # Return a 'disabled account' error message
                    return redirect("test")
            else:
                # Return an 'invalid login' error message.
                login_failed = True
                return render(request, 'manageuser/login.html', locals())
    else: 
        form = AuthenticationForm()

    return render(request, 'manageuser/login.html', locals())

def logout_view(request):
    logout(request)
    return redirect("home")
    
def register(request):
    if request.user.is_authenticated():
        return redirect("home")
        
    if request.method == 'POST':
        form = RegisterForm(request.POST) 

        if form.is_valid():

            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            password_bis = form.cleaned_data['password_bis']

            if password != password_bis:
                password_mismatch = True
            else:
                try:
                    user = User.objects.create_user(username, email, password)
                    user.save()
                    user = authenticate(username=username, password=password)
                    login(request, user)
                except IntegrityError:
                    registration_failed = True
                    return render(request, 'manageuser/register.html', locals())
                return redirect("home")

    else: 
        form = RegisterForm()

    return render(request, 'manageuser/register.html', locals())

def logout_view(request):
    logout(request)
    return redirect("home")

