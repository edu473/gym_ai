from django.urls import path, include
from .views import (
    ListaSesionesView, 
    DetalleSesionView, 
    AgregarRegistroView,
    UserProfileView,
    CrearPlanView,
    dashboard,
    SignUpView,
    EjercicioListView,
    ProgressView,
    EjercicioDetailView,
    SessionAssistantView,
    finalizar_sesion
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('sesiones/', ListaSesionesView.as_view(), name='lista-sesiones'),
    path('sesion/<int:pk>/', DetalleSesionView.as_view(), name='detalle-sesion'),
    path('asistente-sesion/<int:pk>/', SessionAssistantView.as_view(), name='asistente-sesion'),
    path('finalizar-sesion/<int:pk>/', finalizar_sesion, name='finalizar-sesion'),
    path('agregar/', AgregarRegistroView.as_view(), name='agregar-registro'),
    path('perfil/', UserProfileView.as_view(), name='user-profile'),
    path('crear-plan/', CrearPlanView.as_view(), name='crear-plan'),
    path('ejercicios/', EjercicioListView.as_view(), name='lista-ejercicios'),
    path('ejercicio/<int:pk>/', EjercicioDetailView.as_view(), name='detalle-ejercicio'),
    path('progreso/', ProgressView.as_view(), name='progreso'),
]