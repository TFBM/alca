#-*- coding: utf-8 -*-
from django.shortcuts import render
    
def home(request):
    return render(request, 'home/index.html', locals())

def test(request):
    return render(request, 'home/design.html', locals())
