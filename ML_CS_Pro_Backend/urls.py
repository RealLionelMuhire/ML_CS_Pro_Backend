# ML_CS_Pro_Backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("backend/", include("backend.urls")),  # Include the app URLs
]
