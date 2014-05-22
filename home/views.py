#-*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from home.forms import EditUsernameForm
from home.forms import EditEmailForm
from home.forms import EditBitmessageForm
from home.forms import EditPublicKForm
from home.forms import newTransactionForm

from django.db import models

#Added for email server
from django.conf import settings
from django.core.mail import send_mail
    
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
       new_form = newTransactionForm()

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

def disputes(request):
    if request.user.is_authenticated():
       logged = True
       username = request.user.username

    return render(request, 'home/disputes.html', locals())

def new(request):
    if request.method == "POST":
        if "good" and "description" and "price" and "buyer_email" in request.POST:
            form = newTransactionForm(request.POST)
            if form.is_valid():
		message = "Someone want to do a transaction with you. Good : " + form.cleaned_data['good'] + "; Description : " + form.cleaned_data['description'] + "; Price : " + str(form.cleaned_data['price']) + 'Send the ' + time.strftime("%c")
		try : 
			send_mail('CryptoUtc - New Transaction request', message , settings.EMAIL_HOST_USER , [form.cleaned_data['buyer_email']], fail_silently=False)
			
			return redirect("profil")
		except BadHeaderError:
			return HttpResponse('Invalid header found.')
	else :
		return redirect("disputes")
    return redirect("transactions")

