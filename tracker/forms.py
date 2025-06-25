from django import forms
from .models import UserProfile, Ejercicio, RegistroSet

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['peso', 'altura', 'edad', 'nivel_fitness', 'objetivos']

class PlanSemanalForm(forms.Form):
    generar_plan = forms.BooleanField(label="Generar un nuevo plan de entrenamiento semanal", initial=True)

class ProgressForm(forms.Form):
    ejercicio = forms.ModelChoiceField(queryset=None, label="Selecciona un ejercicio")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Obtener los IDs de los ejercicios que el usuario ha registrado
            ejercicio_ids = RegistroSet.objects.filter(sesion__usuario=user).values_list('ejercicio_id', flat=True).distinct()
            # Filtrar el queryset de ejercicios
            self.fields['ejercicio'].queryset = Ejercicio.objects.filter(id__in=ejercicio_ids)
