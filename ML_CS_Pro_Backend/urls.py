# ML_CS_Pro_Backend/urls.py
from django.contrib import admin, auth
from django.urls import include, path

admin.site.site_header = "MLCS Admin"
admin.site.site_title = "MLCS Admin"
admin.site.index_title = "Welcome to MLCS Admin"



urlpatterns = [
    path("admin/", admin.site.urls),
    path("backend/", include("backend.urls")),  # Include the app URLs
]
