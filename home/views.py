#-*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from home.forms import EditUsernameForm
from home.forms import EditEmailForm
from home.forms import EditBitmessageForm
from home.forms import EditPublicKForm
from home.forms import AddPublicKForm
from home.forms import newTransactionForm

from django.db import models
from django.contrib.auth.models import User

#Import database class pubKey
from transactions.models import PubKey

#To create token with email
import hashlib

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
	#Retrieve information of the user
       username = request.user.username
       user_id = request.user.id

       try :
         pubKey = PubKey.objects.get(user = user_id)
       except : 
		   pubKey = 'None'

	# Edit form for modification 
       username_form = EditUsernameForm()
       email_form = EditEmailForm()
       bitmessage_form = EditBitmessageForm()
       publicK_form = EditPublicKForm()
       add_publicK_form = AddPublicKForm()

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
    
def add(request):
    if request.method == "POST":
        if "value" and "name" and "comment" and "order" in request.POST:
            form = AddPublicKForm(request.POST)
            if form.is_valid():
               user_fk = User.objects.get(id=request.user.id)
               p = PubKey(value = form.cleaned_data['value'], name = form.cleaned_data['name'], comment = form.cleaned_data['comment'], order = form.cleaned_data['order'], user = user_fk)
               p.save()
    return redirect("profil")


def new(request):
   if request.method == "POST":
      if "good" and "description" and "price" and "buyer_email" in request.POST:
         form = newTransactionForm(request.POST)
         if form.is_valid():
		      message = "Someone want to do a transaction with you. Good : " + form.cleaned_data['good'] + "; Description : " + form.cleaned_data['description'] + "; Price : " + str(form.cleaned_data['price']) + ", Token : " + hashlib.md5(form.cleaned_data['buyer_email']).hexdigest()
		      #transaction = Transaction(good = form.cleaned_data['good'], description = form.cleaned_data['description'], price =  , pubkey = )
		      try : 
			      send_mail('CryptoUtc - New Transaction request', message , settings.EMAIL_HOST_USER , [form.cleaned_data['buyer_email']], fail_silently=False)
			
			      return redirect("profil")
		      except BadHeaderError:
			      return HttpResponse('Invalid header found.')
      else :
		   return redirect("disputes")
   return redirect("transactions")

