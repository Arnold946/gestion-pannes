from django.db import models

# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Unite(models.Model):
    name = models.CharField(max_length=128, unique=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='unites')

    def __str__(self):
        return self.name
