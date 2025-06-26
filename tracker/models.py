from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Modelo para el perfil del usuario
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    peso = models.DecimalField(max_digits=5, decimal_places=2, help_text="Peso corporal en kg", null=True, blank=True)
    altura = models.DecimalField(max_digits=5, decimal_places=2, help_text="Altura en cm", null=True, blank=True)
    edad = models.PositiveIntegerField(help_text="Edad en años", null=True, blank=True)
    
    NIVEL_FITNESS_CHOICES = [
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ]
    nivel_fitness = models.CharField(
        max_length=20,
        choices=NIVEL_FITNESS_CHOICES,
        default='principiante',
        help_text="Nivel de fitness actual"
    )
    objetivos = models.TextField(help_text="Metas de fitness del usuario", null=True, blank=True)

    def __str__(self):
        return self.user.username

# Modelo para los Ejercicios
class Ejercicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre del ejercicio")
    descripcion = models.TextField(help_text="Descripción detallada del ejercicio", null=True, blank=True)
    muscle_group = models.CharField(max_length=50, help_text="Grupo muscular principal", null=True, blank=True)

    def __str__(self):
        return self.nombre

# Modelo para el Plan Semanal (generado por IA)
class PlanSemanal(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Plan para {self.usuario.username} ({self.fecha_inicio} - {self.fecha_fin})"

# Modelo para un día específico del plan
class DiaPlan(models.Model):
    plan = models.ForeignKey(PlanSemanal, on_delete=models.CASCADE, related_name='dias')
    dia_semana = models.CharField(max_length=10, help_text="Ej: Lunes, Martes...")

    def __str__(self):
        return f"{self.dia_semana} - {self.plan}"

# Modelo para un ejercicio específico en un día del plan
class EjercicioPlan(models.Model):
    dia_plan = models.ForeignKey(DiaPlan, on_delete=models.CASCADE, related_name='ejercicios')
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    series = models.PositiveIntegerField()
    repeticiones = models.CharField(max_length=20) # Ej: "8-12" o "15"
    peso_recomendado = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.ejercicio.nombre} ({self.series}x{self.repeticiones})"

# Modelo para la Sesión de Entrenamiento
class SesionEntrenamiento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    fecha = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Sesión de {self.usuario.username} - {self.fecha.strftime('%d-%m-%Y')}"

# Modelo para el Registro de una Serie
class RegistroSet(models.Model):
    sesion = models.ForeignKey(SesionEntrenamiento, on_delete=models.CASCADE, related_name='registros')
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    repeticiones = models.PositiveIntegerField()
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    # Nuevo campo para el temporizador
    tiempo_descanso = models.PositiveIntegerField(help_text="Tiempo de descanso en segundos", null=True, blank=True)


    def __str__(self):
        return f'{self.ejercicio.nombre} - {self.repeticiones} reps @ {self.peso} kg'
