#-*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from home.forms import EditUsernameForm, EditEmailForm, EditBitmessageForm, EditPublicKForm, AddPublicKForm, newTransactionForm
from django.db import models
from django.contrib.auth.models import User

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
  try:
    pubKey = PubKey.objects.filter(user=request.user.id).order_by('order')
  except:
    #Todo, faire une page disant d’ajouter une clé 
    pubKey = None


  # Edit form for modification 
  username_form = EditUsernameForm()
  email_form = EditEmailForm()
  bitmessage_form = EditBitmessageForm()
  publicK_form = EditPublicKForm()
  add_publicK_form = AddPublicKForm()

  return render(request, 'home/profil.html', locals())


@login_required
def transactions(request):
  try :
    pubKey = PubKey.objects.filter(user = request.user.id).order_by('order')
  except:
    #Todo: renvoyer sur la page permettant de créer une clé avec un message disant de le faire
    pubKey = None

  new_form = newTransactionForm(pubKey=pubKey)

  return render(request, 'home/transactions.html', locals())

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

@login_required
@require_POST
def add(request):
  form = AddPublicKForm(request.POST)
  if form.is_valid():
    #Todo vérification de la validité de la clé publique
    user_fk = User.objects.get(id=request.user.id)
    p = PubKey(value = form.cleaned_data['value'], name = form.cleaned_data['name'], comment = form.cleaned_data['comment'], order = form.cleaned_data['order'], user = user_fk)
    p.save()
  return redirect("profil")

@login_required
@require_POST
def new(request):
  try:
    pubKey = PubKey.objects.filter(user=request.user.id).order_by('order')
  except:
    #Todo là encore renvoie vers une page disant d’ajouter une clé publique
    pubKey = None
    
  form = newTransactionForm(request.POST, pubKey=pubKey)

  if form.is_valid():
    seller_pubKey = PubKey.objects.get(value = form.cleaned_data['pubKey'])
    transaction = Transaction(good = form.cleaned_data['good'],
			      description = form.cleaned_data['description'],
			      price = form.cleaned_data['price'] ,
			      seller = seller_pubKey ,
			      datetime_init = datetime.now())
    transaction.save()

    return redirect("profil")
  else:
    return redirect("disputes")
