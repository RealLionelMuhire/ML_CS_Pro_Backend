from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView

from .forms import AdminRegistrationForm, ClientRegistrationForm

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

class AdminLoginView(LoginView):
    template_name = 'registration/admin_login.html'