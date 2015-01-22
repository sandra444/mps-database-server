from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from django.template import RequestContext
# from forms import MyRegistrationForm

import os
import settings

def main(request):
    c = RequestContext(request)
    return render_to_response('index.html', c)

def login(request):
    # Don't allow a user to try to log in twice
    if request.user.is_active:
        return HttpResponseRedirect("/")
    c = RequestContext(request)
    c.update(csrf(request))
    c.update({'next':request.GET.get('next', '')})
    return render_to_response('login.html', c)

def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    next = request.POST.get('next', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        if next:
            return HttpResponseRedirect(next)
        else:
            return HttpResponseRedirect('/accounts/loggedin')
    else:
        return HttpResponseRedirect('/accounts/invalid')

def loggedin(request):
    c = RequestContext(request)
    c.update({'full_name': request.user.username})
    return render_to_response('loggedin.html', c)

def invalid_login(request):
    c = RequestContext(request)
    return render_to_response('invalid_login.html', c)

def logout(request):
    auth.logout(request)
    c = RequestContext(request)
    return render_to_response('logout.html', c)
