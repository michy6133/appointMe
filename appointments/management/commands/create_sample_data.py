from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from appointments.models import Customer, Service, Appointment, BusinessHours, Staff
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Crée des données d\'exemple pour l\'application'

    def handle(self, *args, **options):
        self.stdout.write('Création des données d\'exemple...')

        # Créer un utilisateur admin si il n'existe pas
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@appointme.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write('Utilisateur admin créé (admin/admin123)')

        # Créer des services
        services_data = [
            {'name': 'Consultation générale', 'duration': timedelta(minutes=30), 'price': 50.00},
            {'name': 'Consultation spécialisée', 'duration': timedelta(minutes=45), 'price': 80.00},
            {'name': 'Suivi médical', 'duration': timedelta(minutes=20), 'price': 30.00},
            {'name': 'Urgences', 'duration': timedelta(minutes=15), 'price': 100.00},
        ]

        services = []
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'description': f"Service de {service_data['name'].lower()}",
                    'duration': service_data['duration'],
                    'price': service_data['price'],
                    'is_active': True
                }
            )
            services.append(service)
            if created:
                self.stdout.write(f'Service créé: {service.name}')

        # Créer des clients
        customers_data = [
            {'first_name': 'Jean', 'last_name': 'Dupont', 'email': 'jean.dupont@email.com', 'phone': '+33 1 23 45 67 89'},
            {'first_name': 'Marie', 'last_name': 'Martin', 'email': 'marie.martin@email.com', 'phone': '+33 1 23 45 67 90'},
            {'first_name': 'Pierre', 'last_name': 'Durand', 'email': 'pierre.durand@email.com', 'phone': '+33 1 23 45 67 91'},
            {'first_name': 'Sophie', 'last_name': 'Bernard', 'email': 'sophie.bernard@email.com', 'phone': '+33 1 23 45 67 92'},
            {'first_name': 'Paul', 'last_name': 'Moreau', 'email': 'paul.moreau@email.com', 'phone': '+33 1 23 45 67 93'},
        ]

        customers = []
        for customer_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                email=customer_data['email'],
                defaults=customer_data
            )
            customers.append(customer)
            if created:
                self.stdout.write(f'Client créé: {customer.full_name}')

        # Créer des rendez-vous
        admin_user = User.objects.get(username='admin')
        today = datetime.now().date()
        
        for i in range(20):
            customer = random.choice(customers)
            service = random.choice(services)
            
            # Créer des rendez-vous sur les 30 prochains jours
            appointment_date = today + timedelta(days=random.randint(0, 30))
            appointment_time = datetime.combine(
                appointment_date,
                datetime.min.time().replace(hour=random.randint(8, 17), minute=random.choice([0, 15, 30, 45]))
            )
            
            status = random.choice(['scheduled', 'confirmed', 'completed'])
            
            appointment = Appointment.objects.create(
                customer=customer,
                service=service,
                appointment_date=appointment_time,
                duration=service.duration,
                status=status,
                notes=f"Rendez-vous de {service.name} pour {customer.full_name}",
                created_by=admin_user
            )
            
            if i < 5:  # Afficher seulement les 5 premiers
                self.stdout.write(f'Rendez-vous créé: {appointment}')

        # Créer les heures d'ouverture
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        for i, day in enumerate(days):
            is_open = i < 5  # Ouvert du lundi au vendredi
            BusinessHours.objects.get_or_create(
                day=day,
                defaults={
                    'is_open': is_open,
                    'open_time': '09:00' if is_open else '09:00',
                    'close_time': '18:00' if is_open else '12:00',
                    'lunch_start': '12:00' if is_open else None,
                    'lunch_end': '14:00' if is_open else None,
                }
            )

        self.stdout.write(
            self.style.SUCCESS('Données d\'exemple créées avec succès!')
        )
        self.stdout.write('Vous pouvez maintenant vous connecter avec admin/admin123')
