#-*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from home.forms import EditUsernameForm
from home.forms import EditEmailForm
from home.forms import EditBitmessageForm
from home.forms import EditPublicKForm
    
def home(request):
    if request.user.is_authenticated():
       logged = True
       username = request.user.username
        
    return render(request, 'home/index.html', locals())

def profil(request):
    if request.user.is_authenticated():
       logged = True
       username = request.user.username
       username_form = EditUsernameForm()
       email_form = EditEmailForm()
       bitmessage_form = EditBitmessageForm()
       publicK_form = EditPublicKForm()

    return render(request, 'home/profil.html', locals())

def transactions(request):
    if request.user.is_authenticated():
       logged = True
       username = request.user.username

    return render(request, 'home/transactions.html', locals())

def edit(request):
    if request.method == "POST":
        if "username" in request.POST:
            form = EditUsernameForm(request.POST)
            if form.is_valid():
                request.user.username = form.cleaned_data['username']
                request.user.save()
	if "email" in request.POST:
	    form = EditEmailForm(request.POST)
	    if form.is_valid():
		request.user.email = form.cleaned_data['email']
                request.user.save()
    return redirect("profil")
    
