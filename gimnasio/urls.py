from django.contrib import admin
from django.urls import path, include  # Asegúrate de que 'include' esté importado

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esta línea le dice al proyecto que cualquier URL que no sea 'admin/'
    # debe ser manejada por el archivo urls.py de la aplicación 'tracker'.
    path('', include('tracker.urls')),
]