from django.db import models
from organisation.models import Unite

# Create your models here.
class CategorieMateriel(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name



class Materiel(models.Model):
    name = models.CharField(max_length=128)
    numero_serie = models.CharField(max_length=128, unique=True)
    categorie = models.ForeignKey(CategorieMateriel, on_delete=models.CASCADE, blank=True, null=True, default=1)
    unite = models.ForeignKey(Unite, on_delete=models.CASCADE, blank=True, null=True)
    date_acquisition = models.DateField()
    en_service = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='materiels/', blank=True, null=True)

    def __str__(self):
        return self.name