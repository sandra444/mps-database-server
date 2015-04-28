from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from django.template import RequestContext
from forms import SearchForm

import os
import settings

def main(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            return search(request)

    else:
        form = SearchForm(initial={'app': 'Compounds'})

    c = RequestContext(request)
    c.update({'form':form})
    return render_to_response('index.html', c)

def login(request):
    next = request.GET.get('next', '')
    # Don't allow a user to try to log in twice
    if request.user.is_active:
        # Redirect if already logged in and next in GET
        if next:
            return HttpResponseRedirect(next)
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

def search(request):
    app = request.POST.get('app','')
    search_term = request.POST.get('search_term', '')

    bioactivities = {
        'compound': request.POST.get('compound', ''),
        'target': request.POST.get('target', ''),
        'name': request.POST.get('name', ''),
        'pubchem': request.POST.get('pubchem', ''),
        'exclude_targetless': request.POST.get('exclude_targetless', ''),
        'exclude_organismless': request.POST.get('exclude_organismless', ''),
    }

    # If there is not a specified app, just return to the home page
    if not app:
        return HttpResponseRedirect('/')

    elif app == 'Compounds':
        return HttpResponseRedirect('/compounds/?search={}'.format(search_term))

    elif app == 'Drug Trials':
        return HttpResponseRedirect('/drugtrials/?search={}'.format(search_term))

    elif app == 'Adverse Events':
        return HttpResponseRedirect('/adverse_events/?search={}'.format(search_term))

    elif app == 'Bioactivities':
        search_term = [(term + '=' + bioactivities.get(term)) for term in bioactivities if bioactivities.get(term)]
        search_term = '&'.join(search_term)
        return HttpResponseRedirect('/bioactivities/?{}'.format(search_term))

    elif app == 'Studies':
        return HttpResponseRedirect('/assays/organchipstudy/?search={}'.format(search_term))

    # If, for whatever reason, invalid data is entered, just return to the home page
    else:
        return HttpResponseRedirect('/')

