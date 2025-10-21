from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Customer(models.Model):
    """Modèle pour les clients"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Service(models.Model):
    """Modèle pour les services proposés"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    duration = models.DurationField(help_text="Durée du service en minutes")
    price = models.DecimalField(max_digits=10, decimal_places=0, help_text="Prix en Francs CFA")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_services')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    """Modèle pour les rendez-vous"""
    STATUS_CHOICES = [
        ('scheduled', 'Programmé'),
        ('confirmed', 'Confirmé'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
        ('no_show', 'Absent'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    duration = models.DurationField(help_text="Durée du rendez-vous")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['appointment_date']

    def __str__(self):
        return f"{self.customer.full_name} - {self.service.name} - {self.appointment_date.strftime('%d/%m/%Y %H:%M')}"

    @property
    def is_today(self):
        return self.appointment_date.date() == timezone.now().date()

    @property
    def is_past(self):
        return self.appointment_date < timezone.now()

    @property
    def is_upcoming(self):
        return self.appointment_date > timezone.now()


class AppointmentReminder(models.Model):
    """Modèle pour les rappels de rendez-vous"""
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_date = models.DateTimeField()
    sent = models.BooleanField(default=False)
    reminder_type = models.CharField(max_length=50, choices=[
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('call', 'Appel'),
    ], default='email')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rappel pour {self.appointment} - {self.reminder_date}"


class BusinessHours(models.Model):
    """Modèle pour les heures d'ouverture"""
    DAY_CHOICES = [
        ('monday', 'Lundi'),
        ('tuesday', 'Mardi'),
        ('wednesday', 'Mercredi'),
        ('thursday', 'Jeudi'),
        ('friday', 'Vendredi'),
        ('saturday', 'Samedi'),
        ('sunday', 'Dimanche'),
    ]

    day = models.CharField(max_length=10, choices=DAY_CHOICES, unique=True)
    is_open = models.BooleanField(default=True)
    open_time = models.TimeField()
    close_time = models.TimeField()
    lunch_start = models.TimeField(blank=True, null=True)
    lunch_end = models.TimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_business_hours')

    def __str__(self):
        return f"{self.get_day_display()} - {'Ouvert' if self.is_open else 'Fermé'}"


class Staff(models.Model):
    """Modèle pour le personnel"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    specializations = models.ManyToManyField(Service, blank=True, related_name='staff')
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"