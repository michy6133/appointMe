from django.contrib import admin
from .models import Customer, Service, Appointment, AppointmentReminder, BusinessHours, Staff


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering = ['last_name', 'first_name']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'service', 'appointment_date', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'appointment_date', 'created_at']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__email', 'service__name']
    ordering = ['-appointment_date']
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('customer', 'service', 'appointment_date', 'duration', 'status')
        }),
        ('Détails', {
            'fields': ('notes', 'created_by')
        }),
    )


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'reminder_date', 'reminder_type', 'sent', 'created_at']
    list_filter = ['sent', 'reminder_type', 'created_at']
    search_fields = ['appointment__customer__first_name', 'appointment__customer__last_name']
    ordering = ['-reminder_date']


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ['day', 'is_open', 'open_time', 'close_time', 'lunch_start', 'lunch_end']
    list_filter = ['is_open', 'day']
    ordering = ['day']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']
    filter_horizontal = ['specializations']