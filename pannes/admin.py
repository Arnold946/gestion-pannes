from django.contrib import admin

from pannes.models import Panne


# Register your models here.
@admin.register(Panne)
class PanneAdmin(admin.ModelAdmin):
    list_display = ['id', 'titre','materiel','user']

