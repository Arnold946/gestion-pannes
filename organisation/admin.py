from django.contrib import admin
from organisation.models import Service, Unite

# Register your models here.
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    list_filter = ['name']

@admin.register(Unite)
class UniteAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'service']
    search_fields = ['name']
    list_filter = ['service']