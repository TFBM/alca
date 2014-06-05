#-*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from home.forms import EditUsernameForm, EditEmailForm, EditBitmessageForm, EditPublicKForm, AddPublicKForm
from django.db import models
from django.contrib.auth.models import User
from django.contrib import messages

#Import database class pubKey
from transactions.models import PubKey, Transaction

#Import time to get the time at creation of the transaction
from datetime import datetime

#To create token with email
import hashlib

#Added for email server
from django.conf import settings
from django.core.mail import send_mail
    
def home(request):
    return render(request, 'home/index.html', locals())

@login_required
def profil(request):
  #Retrieve information of the user
  pubKey = PubKey.objects.filter(user=request.user.id)
  print pubKey
  if len(pubKey) == 0:
    messages.warning(request, "It seems you do not have entered a public key. You cannot create transactions yet.")


  # Edit form for modification 
  username_form = EditUsernameForm()
  email_form = EditEmailForm()
  bitmessage_form = EditBitmessageForm()
  publicK_form = EditPublicKForm()
  add_publicK_form = AddPublicKForm()

  return render(request, 'home/profil.html', locals())


@login_required
@require_POST
def add(request):
  form = AddPublicKForm(request.POST)
  if form.is_valid():
    #Todo vérification de la validité de la clé publique
    user_fk = User.objects.get(id=request.user.id)

    if form.cleaned_data['default']:
      try :
        pubKey = PubKey.objects.get(user=request.user.id, default=True) #Forcément unique
      except :
        messages.warning(request, "You cannot have two default public keys")

      if pubKey :
        pubKey.default = False
        pubKey.save()
    
    p = PubKey(value = form.cleaned_data['value'],
               name = form.cleaned_data['name'],
               comment = form.cleaned_data['comment'], default = form.cleaned_data['default'],
               user = user_fk)
    p.save()
  return redirect("profil")

@login_required
@require_POST
def edit(request):
  form = EditUsernameForm(request.POST)
  if form.is_valid():
    request.user.username = form.cleaned_data['username']
    request.user.save()
      
  form = EditEmailForm(request.POST)
  if form.is_valid():
    request.user.email = form.cleaned_data['email']
    request.user.save()
  return redirect("profil")

@login_required
def disputes(request):
    return render(request, 'home/disputes.html', locals())


