from django.contrib import admin

from pannes.models import Panne, AffectationPanne, Notification


# Register your models here.
@admin.register(Panne)
class PanneAdmin(admin.ModelAdmin):
    list_display = ['id', 'titre','materiel','user']

@admin.register(AffectationPanne)
class AffectationPanneAdmin(admin.ModelAdmin):
    list_display = ['id','panne','technicien']


@admin.register(Notification)
class NontificationAdmin(admin.ModelAdmin):
    list_display = ['id','panne','utilisateur','message','date_envoi']
