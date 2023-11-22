from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .forms import AdminRegistrationForm, ClientRegistrationForm

from .forms import AdminRegistrationForm, ClientRegistrationForm

def home(request):
    return render(request, 'home.html')

def register_admin(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('admin_dashboard')
    else:
        form = AdminRegistrationForm()

    return render(request, 'registration/admin_register.html', {'form': form})

def register_client(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('client_dashboard')
        form = ClientRegistrationForm()

    return render(request, 'registration/client_register.html', {'form': form})
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

class AdminLoginView(LoginView):
    template_name = 'registration/admin_login.html'

class ClientLoginView(LoginView):
    template_name = 'registration/client_login.html'

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def hello_world(request):
    return JsonResponse({'message': 'Hello, World!'})