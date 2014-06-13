from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from manageuser.forms import AuthenticationForm, RegisterForm
from django.db import IntegrityError
from django.contrib import messages
from transactions.models import Transaction

def login_view(request):


    #On recupere le token dans l'url
    if request.GET.get('token',None) :
      request.session['token'] = request.GET.get('token',None)
    
    token = request.session.get('token', None)
    
    if request.user.is_authenticated():
    #On verifie qu'il y a un token si oui on enregistre le user id a la transaction
      if token is not None :
        transaction = Transaction.objects.get(token=token)
        transaction.buyer_id = request.user
        transaction.save()
        return redirect("transactions")
      else :
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
                    if token is not None :
                      transaction = Transaction.objects.get(token=token)
                      transaction.buyer_id = request.user
                      transaction.save()
                      return redirect("transactions")
                    else :
                      return redirect("profil")
                else:
                    messages.error(request, "Account deactivated")
                    logout(request)
                    return redirect("home")
            else:
                messages.error(request, "Bad credentials")
                return render(request, 'manageuser/login.html', locals())
    else: 
        form = AuthenticationForm()

    return render(request, 'manageuser/login.html', locals())

def logout_view(request):
    logout(request)
    return redirect("home")
    
def register(request):

    token = request.session.get('token', None)

    if request.user.is_authenticated():
        return redirect("profile")
        
    if request.method == 'POST':
        form = RegisterForm(request.POST) 

        if form.is_valid():

            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            password_bis = form.cleaned_data['password_bis']

            if "@" in username:
                messages.warning(request, "You cannot have '@' in your username")
                return redirect("home")

            if password != password_bis:
                messages.error(request, "The passwords you typed did not matched")
            else:
                try:
                    user = User.objects.create_user(username, email, password)
                    user.save()
                    user = authenticate(username=username, password=password)
                    login(request, user)
                except IntegrityError:
                    messages.error(request, "Unable to register your account")
                    return render(request, 'manageuser/register.html', locals())
                if token is not None :
                  transaction = Transaction.objects.get(token=token)
                  transaction.buyer_id = user
                  transaction.save()
                  return redirect("transactions")  
                else :    
                  return redirect("profile")

    else: 
        form = RegisterForm()

    return render(request, 'manageuser/register.html', locals())

def logout_view(request):
    logout(request)
    return redirect("home")

