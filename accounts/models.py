from django.db import models
from django.contrib.auth.models import AbstractUser
from organisation.models import Service, Unite

# Create your models here.
class Role(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

class Interface(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name
    
class PermissionInterface(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    peut_voir = models.BooleanField(default=False)
    peut_modifier = models.BooleanField(default=False)
    peut_supprimer = models.BooleanField(default=False)
    peut_ajouter = models.BooleanField(default=False)
    peut_telecharger = models.BooleanField(default=False)
    peut_imprimer = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'interface')
    
    def __str__(self):
        return f"{self.role.name} - {self.interface.name}"
    
class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(unique=True)
    unite = models.ForeignKey(Unite, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    doit_changer_mot_de_passe = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']




