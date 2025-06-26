import datetime
import json
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, ListView
from .forms import PlanSemanalForm, UserProfileForm, ProgressForm
from .models import (DiaPlan, Ejercicio, EjercicioPlan, PlanSemanal,
                     RegistroSet, SesionEntrenamiento, UserProfile)

import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        UserProfile.objects.create(user=user)
        return redirect('dashboard')

class ListaSesionesView(LoginRequiredMixin, ListView):
    model = SesionEntrenamiento
    template_name = 'tracker/lista_sesiones.html'
    context_object_name = 'sesiones'

    def get_queryset(self):
        return SesionEntrenamiento.objects.filter(usuario=self.request.user).order_by('-fecha')

class DetalleSesionView(LoginRequiredMixin, DetailView):
    model = SesionEntrenamiento
    template_name = 'tracker/detalle_sesion.html'
    context_object_name = 'sesion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registros'] = RegistroSet.objects.filter(sesion=self.object).order_by('ejercicio__nombre')
        return context

class EjercicioListView(LoginRequiredMixin, ListView):
    model = Ejercicio
    template_name = 'tracker/ejercicio_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ejercicios = context['object_list']
        ejercicios_agrupados = {}
        for ejercicio in ejercicios:
            if ejercicio.muscle_group not in ejercicios_agrupados:
                ejercicios_agrupados[ejercicio.muscle_group] = []
            ejercicios_agrupados[ejercicio.muscle_group].append(ejercicio)
        context['ejercicios_agrupados'] = ejercicios_agrupados
        return context

    def get_queryset(self):
        ejercicios = super().get_queryset()
        for ejercicio in ejercicios:
            if not ejercicio.descripcion or not ejercicio.muscle_group:
                try:
                    genai.configure(api_key=os.environ.get('api_key'))
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    if not ejercicio.descripcion:
                        prompt = f"""
                        Proporciona una descripción detallada de cómo realizar el siguiente ejercicio: {ejercicio.nombre}.
                        La descripción debe ser clara, concisa y fácil de entender para un principiante, y debe estar en formato markdown.
                        """
                        response = model.generate_content(prompt)
                        ejercicio.descripcion = response.text
                    if not ejercicio.muscle_group:
                        prompt = f"""
                        ¿Cuál es el grupo muscular principal que trabaja el siguiente ejercicio: {ejercicio.nombre}?
                        Responde solo con el nombre del grupo muscular (ej: Pecho, Espalda, Piernas, etc.).
                        """
                        response = model.generate_content(prompt)
                        ejercicio.muscle_group = response.text.strip()
                    ejercicio.save()
                except Exception as e:
                    print(f"Error al generar datos para {ejercicio.nombre}: {e}")
        return ejercicios

class EjercicioDetailView(LoginRequiredMixin, DetailView):
    model = Ejercicio
    template_name = 'tracker/ejercicio_detail.html'
    context_object_name = 'ejercicio'

class SessionAssistantView(LoginRequiredMixin, DetailView):
    model = SesionEntrenamiento
    template_name = 'tracker/session_assistant.html'
    context_object_name = 'sesion'

@login_required
def finalizar_sesion(request, pk):
    sesion = SesionEntrenamiento.objects.get(pk=pk)
    # Here you can add any logic to save the session details
    # For example, you could mark the session as completed
    return redirect('lista-sesiones')




class AgregarRegistroView(LoginRequiredMixin, CreateView):
    model = RegistroSet
    fields = ['ejercicio', 'repeticiones', 'peso', 'tiempo_descanso']
    template_name = 'tracker/agregar_registro.html'
    
    def form_valid(self, form):
        sesion_hoy, created = SesionEntrenamiento.objects.get_or_create(
            usuario=self.request.user, 
            fecha=datetime.date.today()
        )
        form.instance.sesion = sesion_hoy
        super().form_valid(form)
        return redirect('detalle-sesion', pk=sesion_hoy.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ejercicios'] = Ejercicio.objects.all()
        return context

class UserProfileView(LoginRequiredMixin, FormView):
    template_name = 'tracker/user_profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('user-profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'], created = UserProfile.objects.get_or_create(user=self.request.user)
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class ProgressView(LoginRequiredMixin, FormView):
    template_name = 'tracker/progress.html'
    form_class = ProgressForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        ejercicio = form.cleaned_data['ejercicio']
        registros = RegistroSet.objects.filter(sesion__usuario=self.request.user, ejercicio=ejercicio).order_by('sesion__fecha')
        
        fechas = [r.sesion.fecha.strftime('%Y-%m-%d') for r in registros]
        pesos = [float(r.peso) for r in registros]
        
        context = self.get_context_data(
            form=form,
            ejercicio_seleccionado=ejercicio,
            fechas_json=json.dumps(fechas),
            pesos_json=json.dumps(pesos)
        )
        return self.render_to_response(context)

class CrearPlanView(LoginRequiredMixin, FormView):
    template_name = 'tracker/crear_plan.html'
    form_class = PlanSemanalForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        
        prompt = """
        Crea un plan de entrenamiento de gimnasio para un usuario con las siguientes características:
        - Peso: {} kg
        - Altura: {} cm
        - Edad: {} años
        - Nivel de fitness: {}
        - Objetivos: {}

        El plan debe ser para 5 días a la semana (Lunes a Viernes).
        Genera el plan en formato JSON con la siguiente estructura:
        {{
            "dias": [
                {{
                    "dia_semana": "Lunes",
                    "ejercicios": [
                        {{
                            "nombre": "Nombre del Ejercicio",
                            "series": 4,
                            "repeticiones": "8-12",
                            "descripcion": "Descripción detallada del ejercicio en formato markdown"
                        }}
                    ]
                }}
            ]
        }}
        """.format(
            user_profile.peso,
            user_profile.altura,
            user_profile.edad,
            user_profile.get_nivel_fitness_display(),
            user_profile.objetivos
        )
        
        try:
            # Configure your Gemini API key here. Remember to keep it secret.
            genai.configure(api_key=os.environ.get('api_key'))

            model = genai.GenerativeModel('gemini-2.5-flash')
            
            response = model.generate_content(prompt)
            
            # Clean up the response to remove markdown and parse JSON
            cleaned_response = response.text.strip().lstrip("```json").rstrip("```")
            plan_generado = json.loads(cleaned_response)
            self.guardar_plan(plan_generado)
            
        except Exception as e:
            # Handle API errors or JSON parsing errors
            print(f"Error al generar el plan: {e}")
            # Optionally, add a message to the user
            # messages.error(self.request, "Hubo un error al generar el plan. Inténtalo de nuevo.")
            return self.form_invalid(form)

        return super().form_valid(form)

    def guardar_plan(self, plan_data):
        PlanSemanal.objects.filter(usuario=self.request.user).update(activo=False)

        today = datetime.date.today()
        plan = PlanSemanal.objects.create(
            usuario=self.request.user,
            fecha_inicio=today,
            fecha_fin=today + datetime.timedelta(days=6),
            activo=True
        )

        for dia_data in plan_data.get('dias', []):
            dia_plan = DiaPlan.objects.create(plan=plan, dia_semana=dia_data['dia_semana'])
            for ej_data in dia_data.get('ejercicios', []):
                ejercicio, _ = Ejercicio.objects.get_or_create(nombre=ej_data['nombre'])
                EjercicioPlan.objects.create(
                    dia_plan=dia_plan,
                    ejercicio=ejercicio,
                    series=ej_data['series'],
                    repeticiones=ej_data['repeticiones']
                )

@login_required
def dashboard(request):
    plan_activo = PlanSemanal.objects.filter(usuario=request.user, activo=True).first()
    
    # Datos para el gráfico de progreso
    sesiones = SesionEntrenamiento.objects.filter(usuario=request.user).order_by('fecha')
    fechas = [sesion.fecha.strftime('%Y-%m-%d') for sesion in sesiones]
    volumenes = []
    for sesion in sesiones:
        volumen_sesion = sum(registro.repeticiones * registro.peso for registro in sesion.registros.all())
        volumenes.append(float(volumen_sesion))
        
    context = {
        'plan': plan_activo,
        'fechas_json': json.dumps(fechas),
        'volumenes_json': json.dumps(volumenes),
    }
    return render(request, 'tracker/dashboard.html', context)