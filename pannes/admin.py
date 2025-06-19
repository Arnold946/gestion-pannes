from django.contrib import admin

from pannes.models import Panne, AffectationPanne


# Register your models here.
@admin.register(Panne)
class PanneAdmin(admin.ModelAdmin):
    list_display = ['id', 'titre','materiel','user']

@admin.register(AffectationPanne)
class AffectationPanneAdmin(admin.ModelAdmin):
    list_display = ['id','panne','technicien']