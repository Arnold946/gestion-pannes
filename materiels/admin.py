from django.contrib import admin

from materiels.models import Materiel, CategorieMateriel


# Register your models here.
@admin.register(Materiel)
class MaterielAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'unite']

@admin.register(CategorieMateriel)
class CategorieMaterielAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']