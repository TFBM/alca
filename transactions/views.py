#-*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from transactions.models import PubKey, PubkeyEscrow, Transaction
from transactions.forms import newTransactionForm
from datetime import datetime
import hashlib
from django.conf import settings
from django.core.mail import send_mail

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
def new(request):
  try:
    pubKey = PubKey.objects.filter(user=request.user.id).order_by('order')
  except:
    #Todo là encore renvoie vers une page disant d’ajouter une clé publique
    pubKey = None
    
  form = newTransactionForm(request.POST, pubKey=pubKey)

  if form.is_valid():
    seller_pubKey = PubKey.objects.get(value = form.cleaned_data['pubKey'])
    #TODO Il faudrait un petit algo qui va choisir des clé publique au hasard non utilisé. Pour l'instant on prend tjrs la meme.
    escrow_pubKey = PubkeyEscrow.objects.get(value='03355bc5d353e23ac5df9d1b2931f2d1c2fa931d2b5ee88154f3e963e752372c43')
    transaction = Transaction(good = form.cleaned_data['good'],
			      description = form.cleaned_data['description'],
			      price = form.cleaned_data['price'] ,
			      seller = seller_pubKey ,
			      escrow = escrow_pubKey ,
			      datetime_init = datetime.now(),
			      status = 1)
    transaction.save()

    return redirect("profil")
  else:
    return redirect("disputes")

 
