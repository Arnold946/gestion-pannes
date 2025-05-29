from django.contrib import admin
from accounts.models import Interface, PermissionInterface, Role, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Interface)
class InterfaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(PermissionInterface)
class PermissionInterfaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'role', 'interface',
                     'peut_voir', 'peut_modifier', 
                     'peut_supprimer', 'peut_ajouter',
                       'peut_telecharger', 'peut_imprimer']
    list_filter = ['role', 'interface']
    search_fields = ['role', 'interface']

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'username', 'email', 'role', 'is_active', 'is_staff']
    search_fields = ['username', 'email']
    list_filter = ['role']
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role', 'unite', 'profile_picture', 'phone_number', 'doit_changer_mot_de_passe')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'unite', 'profile_picture', 'phone_number', 'doit_changer_mot_de_passe')}),
    )
    ordering = ['email']