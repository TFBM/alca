#-*- coding: utf-8 -*-
from django.shortcuts import render
    
def home(request):
    if request.user.is_authenticated():
       logged = True
       username = request.user.username
        
    return render(request, 'home/index.html', locals())

def profil(request):
    if request.user.is_authenticated():
       logged = True
       username = request.user.username

    return render(request, 'home/profil.html', locals())

def transactions(request):
    if request.user.is_authenticated():
       logged = True
       username = request.user.username

    return render(request, 'home/transactions.html', locals())
