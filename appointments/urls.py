from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentification
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Pages principales
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('appointments/', views.appointments_view, name='appointments'),
    path('customers/', views.customers_view, name='customers'),
    
    # Gestion des rendez-vous
    path('appointments/create/', views.create_appointment_view, name='create_appointment'),
    path('appointments/<int:appointment_id>/edit/', views.edit_appointment_view, name='edit_appointment'),
    path('appointments/<int:appointment_id>/delete/', views.delete_appointment_view, name='delete_appointment'),
    
    # Gestion des clients
    path('customers/create/', views.create_customer_view, name='create_customer'),
    path('customers/<int:customer_id>/edit/', views.edit_customer_view, name='edit_customer'),
    path('customers/<int:customer_id>/delete/', views.delete_customer_view, name='delete_customer'),
    
    # Gestion des services
    path('services/', views.services_view, name='services'),
    path('services/create/', views.create_service_view, name='create_service'),
    path('services/<int:service_id>/edit/', views.edit_service_view, name='edit_service'),
    path('services/<int:service_id>/delete/', views.delete_service_view, name='delete_service'),
    
    # API
    path('api/appointments/by-date/', views.api_appointments_by_date, name='api_appointments_by_date'),
    path('api/search/', views.global_search, name='global_search'),
    
    # Header functionality
    path('notifications/', views.notifications_view, name='notifications'),
    path('profile/', views.profile_view, name='profile'),
    path('password/change/', auth_views.PasswordChangeView.as_view(template_name='appointments/password_change_form.html', success_url='/password/change/done/'), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='appointments/password_change_done.html'), name='password_change_done'),
]
