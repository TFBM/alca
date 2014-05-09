#-*- coding: utf-8 -*-
from django.shortcuts import render
    
def home(request):
    if request.user.is_authenticated():
       logged = True
       username = request.user.username
        
    return render(request, 'home/index.html', locals())

def test(request):
    return render(request, 'home/design.html', locals())

def profil(request):
    return render(request, 'home/profil.html', locals())
