# backend/customAdmin.py
from django.contrib.auth.views import LoginView
from ..forms import CustomAdminAuthenticationForm

class CustomAdminLoginView(LoginView):
    template_name = 'admin/login.html'  # You may need to adjust the template name
    authentication_form = CustomAdminAuthenticationForm
