from django.contrib import admin
from .models import Ejercicio, SesionEntrenamiento, RegistroSet

# Registramos los modelos para que aparezcan en el panel de administrador.
# Django usará la representación __str__ que definimos en models.py para mostrar los objetos.

admin.site.register(Ejercicio)
admin.site.register(SesionEntrenamiento)
admin.site.register(RegistroSet)