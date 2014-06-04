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
from django.db.models import Q

from django.http import HttpResponse, Http404

@login_required
def transactions(request):

  try:
    pubKey = PubKey.objects.filter(user=request.user.id)
    new_form = newTransactionForm(pubKey=pubKey)
    
  except : 
    new_form = 'Add Key'

  listTransactions = Transaction.objects.all().filter(Q(seller_id=request.user.id) | Q(buyer_id=request.user.id)).order_by('datetime_init').reverse()

  return render(request, 'home/transactions.html', locals())

@login_required
@require_POST
def new(request):
  try:
    pubKey = PubKey.objects.filter(user=request.user.id)
  except:
    #Todo là encore renvoie vers une page disant d’ajouter une clé publique
    pubKey = None
    
  form = newTransactionForm(request.POST, pubKey=pubKey)

  if form.is_valid():
    seller_pubKey = PubKey.objects.get(value = form.cleaned_data['pubKey'])

    #Le transaction_id détermine la clé d’escrow à utiliser, il faut le déterminer
    #de telle manière que :
    #   - il n’ai pas été utilisé auparavant
    #   - il corresponde bien à une clé générée (faut pas créer plus de transactions que de clés)
    #Une seule clé n’existe pour l’instant, correspondant à l’id 0
    transaction_id = 0
    response = requests.get("http://http://91.121.156.63/address/%d" % (transaction_id,))

    if response.status_code != 200:
      #Le backend renvoie une erreur
      return redirect("transactions")

    pubkey = response.json()["key"]
    
    escrow_pubKey = PubkeyEscrow.objects.get(value=pubkey)
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

@login_required
def detail(request, id_transaction):
  
  id = format(id_transaction)
  transaction = Transaction.objects.get(pk=id)
  listPubKey = PubKey.objects.filter(user=request.user.id)
  
  if (transaction.seller in listPubKey) or (transaction.buyer in listPubKey) :     
    return render(request, 'home/transaction_detail.html', locals())
  else :
    return redirect("transactions")
