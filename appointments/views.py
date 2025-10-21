from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import calendar as pycalendar
from django.db.models import Q, Count
from datetime import datetime, timedelta
import json

from .models import Customer, Service, Appointment, BusinessHours, Staff


def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Django utilise username par défaut, mais on peut chercher par email
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')
    
    return render(request, 'appointments/login.html')


def register_view(request):
    """Vue d'inscription"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        
        if password != confirm_password:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'appointments/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Un compte avec cet email existe déjà.')
            return render(request, 'appointments/register.html')
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Créer le profil staff
        Staff.objects.create(
            user=user,
            phone=phone
        )
        
        messages.success(request, 'Compte créé avec succès. Vous pouvez maintenant vous connecter.')
        return redirect('login')
    
    return render(request, 'appointments/register.html')


@login_required
def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    """Vue du tableau de bord"""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    last_week_start = start_of_week - timedelta(days=7)
    last_week_end = end_of_week - timedelta(days=7)
    
    # Statistiques (filtrées par créateur)
    today_appointments = Appointment.objects.filter(
        appointment_date__date=today,
        created_by=request.user
    ).count()
    
    yesterday_appointments = Appointment.objects.filter(
        appointment_date__date=yesterday,
        created_by=request.user
    ).count()
    
    pending_appointments = Appointment.objects.filter(
        status='scheduled',
        created_by=request.user
    ).count()
    
    week_appointments = Appointment.objects.filter(
        appointment_date__date__range=[start_of_week, end_of_week],
        created_by=request.user
    ).count()
    
    last_week_appointments = Appointment.objects.filter(
        appointment_date__date__range=[last_week_start, last_week_end],
        created_by=request.user
    ).count()
    
    total_customers = Customer.objects.filter(created_by=request.user).count()
    
    # Calcul des variations
    today_vs_yesterday = today_appointments - yesterday_appointments
    week_vs_last_week = week_appointments - last_week_appointments
    week_percentage = 0
    if last_week_appointments > 0:
        week_percentage = round((week_vs_last_week / last_week_appointments) * 100)
    
    # Rendez-vous récents (filtrés par créateur)
    recent_appointments = Appointment.objects.filter(
        appointment_date__date=today,
        created_by=request.user
    ).select_related('customer', 'service').order_by('appointment_date')[:5]
    
    # Rendez-vous à venir (filtrés par créateur)
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=timezone.now(),
        created_by=request.user
    ).select_related('customer', 'service').order_by('appointment_date')[:5]
    
    context = {
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'week_appointments': week_appointments,
        'total_customers': total_customers,
        'recent_appointments': recent_appointments,
        'upcoming_appointments': upcoming_appointments,
        'today_vs_yesterday': today_vs_yesterday,
        'week_vs_last_week': week_vs_last_week,
        'week_percentage': week_percentage,
    }
    
    return render(request, 'appointments/dashboard.html', context)


@login_required
def calendar_view(request):
    """Vue du calendrier avec filtres mois/semaine/jour et navigation"""
    mode = request.GET.get('mode', 'month')  # month | week | day
    date_str = request.GET.get('date')  # YYYY-MM-DD

    now = timezone.localtime()
    ref_date = now.date()
    if date_str:
        try:
            ref_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    # Déterminer l'intervalle selon le mode
    if mode == 'day':
        start_date = ref_date
        end_date = ref_date
        prev_date = ref_date - timedelta(days=1)
        next_date = ref_date + timedelta(days=1)
        days = [ref_date]
    elif mode == 'week':
        # Lundi comme début de semaine
        start_date = ref_date - timedelta(days=ref_date.weekday())
        end_date = start_date + timedelta(days=6)
        prev_date = start_date - timedelta(days=7)
        next_date = start_date + timedelta(days=7)
        days = [start_date + timedelta(days=i) for i in range(7)]
    else:
        # Month view par défaut
        first_day = ref_date.replace(day=1)
        _, last_day_num = pycalendar.monthrange(first_day.year, first_day.month)
        last_day = first_day.replace(day=last_day_num)
        start_date = first_day
        end_date = last_day
        # prev/next en mois
        prev_month_year = (first_day.year, first_day.month - 1) if first_day.month > 1 else (first_day.year - 1, 12)
        next_month_year = (first_day.year, first_day.month + 1) if first_day.month < 12 else (first_day.year + 1, 1)
        prev_date = first_day.replace(year=prev_month_year[0], month=prev_month_year[1], day=1)
        next_date = first_day.replace(year=next_month_year[0], month=next_month_year[1], day=1)
        days = [first_day.replace(day=d) for d in range(1, last_day_num + 1)]

    # Récupérer les rendez-vous dans l'intervalle (filtrés par créateur)
    appointments = Appointment.objects.filter(
        appointment_date__date__gte=start_date,
        appointment_date__date__lte=end_date,
        created_by=request.user
    ).select_related('customer', 'service')

    # Grouper par date
    appointments_by_date = {}
    for appointment in appointments:
        date_key = appointment.appointment_date.date()
        appointments_by_date.setdefault(date_key, []).append(appointment)

    # Libellés d'en-tête
    current_month_label = ref_date.strftime('%B %Y')

    # Préparer une structure exploitable dans le template
    days_data = []
    for day in days:
        appts = appointments_by_date.get(day, [])
        days_data.append({
            'date': day,
            'appointments': appts,
        })

    context = {
        'mode': mode,
        'ref_date': ref_date,
        'days_data': days_data,
        'current_month_label': current_month_label,
        'current_year': ref_date.year,
        'current_month': ref_date.strftime('%B'),
        'prev_date': prev_date.strftime('%Y-%m-%d'),
        'next_date': next_date.strftime('%Y-%m-%d'),
        'today_date': now.strftime('%Y-%m-%d'),
    }

    return render(request, 'appointments/calendar.html', context)


@login_required
def appointments_view(request):
    """Vue de gestion des rendez-vous"""
    appointments = Appointment.objects.filter(created_by=request.user).select_related('customer', 'service').order_by('-appointment_date')
    
    # Filtres
    status_filter = request.GET.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    search = request.GET.get('search')
    if search:
        appointments = appointments.filter(
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(customer__email__icontains=search) |
            Q(service__name__icontains=search)
        )
    
    context = {
        'appointments': appointments,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    
    return render(request, 'appointments/appointments.html', context)


@login_required
def customers_view(request):
    """Vue de gestion des clients"""
    customers = Customer.objects.filter(created_by=request.user).order_by('last_name', 'first_name')
    
    # Recherche
    search = request.GET.get('search')
    if search:
        customers = customers.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    context = {
        'customers': customers,
    }
    
    return render(request, 'appointments/customers.html', context)


@login_required
def create_appointment_view(request):
    """Vue de création de rendez-vous"""
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        service_id = request.POST.get('service')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        notes = request.POST.get('notes', '')
        
        try:
            customer = Customer.objects.get(id=customer_id)
            service = Service.objects.get(id=service_id)
            
            # Combiner date et heure
            datetime_str = f"{appointment_date} {appointment_time}"
            appointment_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            appointment_datetime = timezone.make_aware(appointment_datetime)
            
            appointment = Appointment.objects.create(
                customer=customer,
                service=service,
                appointment_date=appointment_datetime,
                duration=service.duration,
                notes=notes,
                created_by=request.user
            )
            
            messages.success(request, 'Rendez-vous créé avec succès.')
            return redirect('appointments')
            
        except (Customer.DoesNotExist, Service.DoesNotExist):
            messages.error(request, 'Client ou service introuvable.')
        except ValueError:
            messages.error(request, 'Format de date/heure invalide.')
    
    customers = Customer.objects.filter(created_by=request.user).order_by('last_name', 'first_name')
    services = Service.objects.filter(is_active=True, created_by=request.user)

    # Pré-remplir la date depuis la query string si fournie
    default_date = request.GET.get('date') or ''
    default_time = ''
    
    context = {
        'customers': customers,
        'services': services,
        'default_date': default_date,
        'default_time': default_time,
    }
    
    return render(request, 'appointments/create_appointment.html', context)


@login_required
def edit_appointment_view(request, appointment_id):
    """Vue de modification de rendez-vous"""
    appointment = get_object_or_404(Appointment, id=appointment_id, created_by=request.user)
    
    if request.method == 'POST':
        appointment.customer_id = request.POST.get('customer')
        appointment.service_id = request.POST.get('service')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        appointment.status = request.POST.get('status')
        appointment.notes = request.POST.get('notes', '')
        
        try:
            # Combiner date et heure
            datetime_str = f"{appointment_date} {appointment_time}"
            appointment_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            appointment.appointment_date = timezone.make_aware(appointment_datetime)
            
            appointment.save()
            messages.success(request, 'Rendez-vous modifié avec succès.')
            return redirect('appointments')
            
        except ValueError:
            messages.error(request, 'Format de date/heure invalide.')
    
    customers = Customer.objects.filter(created_by=request.user).order_by('last_name', 'first_name')
    services = Service.objects.filter(is_active=True, created_by=request.user)
    
    context = {
        'appointment': appointment,
        'customers': customers,
        'services': services,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    
    return render(request, 'appointments/edit_appointment.html', context)


@login_required
def delete_appointment_view(request, appointment_id):
    """Vue de suppression de rendez-vous"""
    appointment = get_object_or_404(Appointment, id=appointment_id, created_by=request.user)
    
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Rendez-vous supprimé avec succès.')
        return redirect('appointments')
    
    return render(request, 'appointments/delete_appointment.html', {'appointment': appointment})


@login_required
def create_customer_view(request):
    """Vue de création de client"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        
        try:
            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address,
                created_by=request.user
            )
            messages.success(request, 'Client créé avec succès.')
            return redirect('customers')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création du client: {str(e)}')
    
    return render(request, 'appointments/create_customer.html')


@login_required
def edit_customer_view(request, customer_id):
    """Vue de modification de client"""
    customer = get_object_or_404(Customer, id=customer_id, created_by=request.user)
    
    if request.method == 'POST':
        customer.first_name = request.POST.get('first_name')
        customer.last_name = request.POST.get('last_name')
        customer.email = request.POST.get('email')
        customer.phone = request.POST.get('phone', '')
        customer.address = request.POST.get('address', '')
        
        try:
            customer.save()
            messages.success(request, 'Client modifié avec succès.')
            return redirect('customers')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification du client: {str(e)}')
    
    return render(request, 'appointments/edit_customer.html', {'customer': customer})


@login_required
def delete_customer_view(request, customer_id):
    """Vue de suppression de client"""
    customer = get_object_or_404(Customer, id=customer_id, created_by=request.user)
    
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Client supprimé avec succès.')
        return redirect('customers')
    
    return render(request, 'appointments/delete_customer.html', {'customer': customer})


# API Views pour AJAX
@login_required
@csrf_exempt
def api_appointments_by_date(request):
    """API pour récupérer les rendez-vous d'une date donnée"""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date manquante'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        appointments = Appointment.objects.filter(
            appointment_date__date=date,
            created_by=request.user
        ).select_related('customer', 'service')
        
        data = []
        for appointment in appointments:
            data.append({
                'id': appointment.id,
                'customer': appointment.customer.full_name,
                'service': appointment.service.name,
                'time': appointment.appointment_date.strftime('%H:%M'),
                'status': appointment.status,
                'status_display': appointment.get_status_display(),
            })
        
        return JsonResponse({'appointments': data})
    except ValueError:
        return JsonResponse({'error': 'Format de date invalide'}, status=400)


@login_required
def global_search(request):
    """Recherche globale dans l'application"""
    query = request.GET.get('q', '').strip()
    results = {
        'appointments': [],
        'customers': [],
        'services': []
    }
    
    if query and len(query) >= 2:
        # Recherche dans les rendez-vous (filtrés par créateur)
        appointments = Appointment.objects.filter(
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query) |
            Q(customer__email__icontains=query) |
            Q(service__name__icontains=query) |
            Q(notes__icontains=query),
            created_by=request.user
        ).select_related('customer', 'service')[:10]
        
        for appointment in appointments:
            results['appointments'].append({
                'id': appointment.id,
                'customer': appointment.customer.full_name,
                'service': appointment.service.name,
                'date': appointment.appointment_date.strftime('%d/%m/%Y %H:%M'),
                'status': appointment.get_status_display(),
                'url': f'/appointments/{appointment.id}/edit/'
            })
        
        # Recherche dans les clients (filtrés par créateur)
        customers = Customer.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query),
            created_by=request.user
        )[:10]
        
        for customer in customers:
            results['customers'].append({
                'id': customer.id,
                'name': customer.full_name,
                'email': customer.email,
                'phone': customer.phone or '',
                'url': f'/customers/{customer.id}/edit/'
            })
        
        # Recherche dans les services (filtrés par créateur)
        services = Service.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            created_by=request.user
        )[:10]
        
        for service in services:
            results['services'].append({
                'id': service.id,
                'name': service.name,
                'duration': str(service.duration),
                'price': str(service.price),
                'url': f'/admin/appointments/service/{service.id}/change/'
            })
    
    return JsonResponse(results)


@login_required
def notifications_view(request):
    """Vue des notifications"""
    # Récupérer les rendez-vous à venir (dans les 7 prochains jours)
    today = timezone.now().date()
    next_week = today + timedelta(days=7)
    
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__date__gte=today,
        appointment_date__date__lte=next_week,
        status__in=['scheduled', 'confirmed'],
        created_by=request.user
    ).select_related('customer', 'service').order_by('appointment_date')
    
    # Rendez-vous en retard (non confirmés depuis plus de 24h)
    yesterday = today - timedelta(days=1)
    overdue_appointments = Appointment.objects.filter(
        appointment_date__date__lt=today,
        status='scheduled',
        created_at__lt=timezone.now() - timedelta(hours=24),
        created_by=request.user
    ).select_related('customer', 'service')
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'overdue_appointments': overdue_appointments,
        'total_notifications': upcoming_appointments.count() + overdue_appointments.count()
    }
    
    return render(request, 'appointments/notifications.html', context)


@login_required
def profile_view(request):
    """Vue du profil utilisateur"""
    if request.method == 'POST':
        # Mise à jour du profil
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Mise à jour du profil staff si il existe
        try:
            staff = user.staff_profile
            staff.phone = request.POST.get('phone', staff.phone)
            # Upload photo
            if 'photo' in request.FILES:
                staff.photo = request.FILES['photo']
            remove_photo = request.POST.get('remove_photo')
            if remove_photo == 'on':
                staff.photo = None
            staff.save()
        except Staff.DoesNotExist:
            # Créer le profil staff si manquant
            staff = Staff.objects.create(user=user, phone=request.POST.get('phone', ''))
            if 'photo' in request.FILES:
                staff.photo = request.FILES['photo']
                staff.save()
        
        messages.success(request, 'Profil mis à jour avec succès.')
        return redirect('profile')
    
    return render(request, 'appointments/profile.html')


@login_required
def services_view(request):
    """Vue de gestion des services"""
    services = Service.objects.filter(created_by=request.user).order_by('name')
    
    # Recherche
    search = request.GET.get('search')
    if search:
        services = services.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    context = {
        'services': services,
    }
    
    return render(request, 'appointments/services.html', context)


@login_required
def create_service_view(request):
    """Vue de création de service"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        duration_hours = int(request.POST.get('duration_hours', 0))
        duration_minutes = int(request.POST.get('duration_minutes', 0))
        price = request.POST.get('price')
        
        try:
            duration = timedelta(hours=duration_hours, minutes=duration_minutes)
            service = Service.objects.create(
                name=name,
                description=description,
                duration=duration,
                price=price,
                created_by=request.user
            )
            messages.success(request, 'Service créé avec succès.')
            return redirect('services')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création du service: {str(e)}')
    
    return render(request, 'appointments/create_service.html')


@login_required
def edit_service_view(request, service_id):
    """Vue de modification de service"""
    service = get_object_or_404(Service, id=service_id, created_by=request.user)
    
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.description = request.POST.get('description', '')
        duration_hours = int(request.POST.get('duration_hours', 0))
        duration_minutes = int(request.POST.get('duration_minutes', 0))
        service.price = request.POST.get('price')
        service.is_active = request.POST.get('is_active') == 'on'
        
        try:
            service.duration = timedelta(hours=duration_hours, minutes=duration_minutes)
            service.save()
            messages.success(request, 'Service modifié avec succès.')
            return redirect('services')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification du service: {str(e)}')
    
    # Convertir la durée en heures et minutes pour l'affichage
    total_minutes = int(service.duration.total_seconds() // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    context = {
        'service': service,
        'duration_hours': hours,
        'duration_minutes': minutes,
    }
    
    return render(request, 'appointments/edit_service.html', context)


@login_required
def delete_service_view(request, service_id):
    """Vue de suppression de service"""
    service = get_object_or_404(Service, id=service_id, created_by=request.user)
    
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service supprimé avec succès.')
        return redirect('services')
    
    return render(request, 'appointments/delete_service.html', {'service': service})