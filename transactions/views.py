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
from django.contrib import messages
import requests
from django.http import HttpResponse, Http404

@login_required
def transactions(request):

  pubKey = PubKey.objects.filter(user=request.user)
  
  new_form = newTransactionForm(pubKey=pubKey)
  if len(pubKey) == 0:
    messages.warning(request, "You must set a public key in order to emit transactions")

  listTransactions = Transaction.objects.all().filter(Q(seller_id=request.user.id) | Q(buyer_id=request.user.id)).order_by('datetime_init').reverse()

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

    #Le transaction_id détermine la clé d’escrow à utiliser, il faut le déterminer
    #de telle manière que :
    #   - il n’ai pas été utilisé auparavant
    #   - il corresponde bien à une clé générée (faut pas créer plus de transactions que de clés)
    #Une seule clé n’existe pour l’instant, correspondant à l’id 0
    transaction_id = 0
    response = requests.get("http://91.121.156.63/address/%d" % (transaction_id,))

    if response.status_code != 200:
      messages.error(request, "Unable to get an escrow key, transaction creation cancelled")
      return redirect("transactions")

    escrow_pubKey = response.json()["key"]

    buyer = form.cleaned_data["buyer"]
    buyer_id = None
    #if "@" not in buyer:
      #buyer_id = User.objects.get(username=buyer)
    
    escrow = PubkeyEscrow(value=escrow_pubKey)
    
    token = hashlib.md5(str(buyer)+str(seller_pubKey)).hexdigest()
    transaction = Transaction(good = form.cleaned_data['good'],
			      description = form.cleaned_data['description'],
			      price = form.cleaned_data['price'] ,
			      seller_key = seller_pubKey,
            seller_id = request.user,
            token = token,
			      escrow = escrow,
			      datetime_init=datetime.now(),
			      status=1)
    transaction.save()
    url = str("http://localhost:8000/accounts/login?token="+token)
    send_mail("[CryptoUTC] - Notification demand transaction", "Someone want to do a transaction with you. Good : "+str(form.cleaned_data['good'])+", description : "+str(form.cleaned_data['description'])+", price : "+str(form.cleaned_data['price'])+", link : "+str(url), settings.DEFAULT_FROM_EMAIL,
    [buyer], fail_silently=False)

    return redirect("profil")
  else:
    message.error(request, "Form invalid")
    return redirect("transactions")

@login_required
def detail(request, id_transaction):
  
  id = format(id_transaction)
  transaction = Transaction.objects.get(pk=id)
  listPubKey = PubKey.objects.filter(user=request.user.id)
  
  if (transaction.seller in listPubKey) or (transaction.buyer in listPubKey) :     
    return render(request, 'home/transaction_detail.html', locals())
  else:
    messages.error(request, "No such transaction")
    return redirect("transactions")
