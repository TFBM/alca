#-*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from transactions.models import PubKey, PubKeyEscrow, Transaction
from transactions.forms import newTransactionForm, acceptTransactionForm
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib import messages
import requests
from django.http import HttpResponse, Http404
import random
import json
from django.core.exceptions import ObjectDoesNotExist

@login_required
def transactions(request):

  pubKey = PubKey.objects.filter(user=request.user)
  
  new_form = newTransactionForm(pubKey=pubKey)
  if len(pubKey) == 0:
    messages.warning(request, "You must set a public key in order to emit transactions")

  listTransactions = Transaction.objects.all().filter(Q(seller_id=request.user.id) | Q(buyer_id=request.user.id)).order_by('datetime_init').reverse()
  for elem in listTransactions : # We add the status display
	  elem.disp_status=elem.get_status_display() 
  
  listTransactionsDemand = Transaction.objects.all().filter(Q(buyer_id=request.user.id) & Q(status=1) & Q(canceled=False)).order_by('datetime_init').reverse()
 
  return render(request, 'home/transactions.html', locals()) 

@login_required
@require_POST
def new(request):
  pubKey = PubKey.objects.filter(user=request.user.id)
  if len(pubKey) == 0:
    messages.warning(request, "You must set a public key in order to emit transactions")
    return redirect("transactions")
  form = newTransactionForm(request.POST, pubKey=pubKey)

  if form.is_valid():
    seller_pubKey = PubKey.objects.get(value = form.cleaned_data['pubKey'])   

    buyer = form.cleaned_data["buyer"]
    buyer_id = None
    if "@" not in buyer:
      buyer_id = User.objects.get(username=buyer)

    transaction = Transaction(good = form.cleaned_data['good'],
			      description = form.cleaned_data['description'],
			      price = form.cleaned_data['price'] ,
			      seller_key = seller_pubKey)

    if buyer_id:
      transaction.buyer_id = buyer_id
      
    transaction.save()
    url = str("http://localhost:8000/accounts/login?token="+transaction.token)
    send_mail("[CryptoUTC] - Notification demand transaction", "Someone want to do a transaction with you. Good : "+str(form.cleaned_data['good'])+", description : "+str(form.cleaned_data['description'])+", price : "+str(form.cleaned_data['price'])+", link : "+str(url), settings.DEFAULT_FROM_EMAIL,[buyer], fail_silently=False)

  else: 
    message.error(request, "Form invalid")
    
  return redirect("transactions")
  


@login_required
def detail(request, id_transaction):
  
  id = format(id_transaction)
  transaction = Transaction.objects.get(pk=id)
  
  if (transaction.seller_id==request.user) or (transaction.buyer_id==request.user):
    redeem = []
    if transaction.redeem_script is not None :
      for i in range(len(transaction.redeem_script)/2):
        redeem.append(transaction.redeem_script[i:i+2])
    return render(request, 'home/transaction_detail.html', locals())
  else:
    messages.error(request, "No such transaction")
    return redirect("transactions")

@login_required
def accept(request, id_transaction):
  
  id = format(id_transaction)
  transaction = Transaction.objects.get(pk=id)
  pubKey = PubKey.objects.all().filter(user=request.user)
  
  if request.method == 'POST' :
    form = acceptTransactionForm(request.POST, pubKey=pubKey)
    if form.is_valid() :
      ret = transaction.creation(PubKey.objects.get(value=form.cleaned_data['pubKey']))
      if ret:
        transaction.save()
      else:
        messages.error(request, "Unable to join backend")
      return redirect("transactions")
  
  if transaction.buyer_id==request.user :
    accept_form = acceptTransactionForm(pubKey=pubKey)
    if pubKey.exists() :    
      return render(request, 'home/transaction_accept.html', locals())
    else :
      messages.error(request,"You need to add a public key in your profil")
      return redirect("profil")
  else:
    messages.error(request, "No such transaction")
    return redirect("transactions")
    
    
@login_required
def cancel(request, id_transaction):
  
  id = format(id_transaction)
  transaction = Transaction.objects.get(pk=id)
  
  if (transaction.seller_id==request.user) or (transaction.buyer_id==request.user) : 
    transaction.cancel()
    transaction.save()  
    return redirect("transactions")
  else:
    messages.error(request, "No such transaction")
    return redirect("transactions")
    
@login_required
def dispute(request, id_transaction):
  
  id = format(id_transaction)
  transaction = Transaction.objects.get(pk=id)
  
  if (transaction.seller_id==request.user) or (transaction.buyer_id==request.user) : 
    return render(request, 'home/dispute_form.html', locals())
  else:
    messages.error(request, "No such transaction")
    return redirect("transactions")

def update_status(request, id_transaction):
#TODO : Authentification pour être sur que c'est l'API qui y accède à cette page
  try :
    id = format(id_transaction)
    transaction = Transaction.objects.get(pk=id)
    if(transaction.status == 2) :
      transaction.payment()
      transaction.save()
      return HttpResponse(content="Status updated !",status=200)
    else :
      if (transaction.status == 4) or (transaction.status == 5 ) :
        transaction.cashout()
        transaction.save()
        return HttpResponse(content="Status updated !",status=200)
      else :
        return HttpResponse(content="The transaction status cannot been updated !",status=418)
  except :
    return HttpResponse(content="Error, status not updated !",status=418)
