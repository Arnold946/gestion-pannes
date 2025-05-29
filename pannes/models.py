from django.db import models
from accounts.models import User
from materiels.models import Materiel

class Panne(models.Model):
    STATUS_CHOICES = [
        ('nouvelle', 'Nouvelle'),
        ('en_cours', 'En cours'),
        ('resolue', 'Résolue'),
        ('fermee', 'Fermée'),
    ]

    PRIORITY_CHOICES = [
        ('haute', 'Haute'),
        ('moyenne', 'Moyenne'),
        ('basse', 'Basse'),  
    ]
    titre = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    date_signalement = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='nouvelle')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='moyenne')
    categorie_materiel = models.ForeignKey('materiels.CategorieMateriel', on_delete=models.CASCADE, related_name='pannes', default=1)
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE, related_name='pannes', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__name':'utilisateur'}, related_name='panne_utilisateur')

    def __str__(self):
        return f'{self.description} - {self.status} - {self.priority} - {self.user.username}'


class AffectationPanne(models.Model):
    panne = models.ForeignKey(Panne, on_delete=models.CASCADE, related_name='affectation_panne')
    technicien = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__name':'technicien'}, related_name='panne_technicien')
    attribue_par = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__name':'chef unite informatique'}, related_name='panne_attribue_par')
    date_affectation = models.DateTimeField(auto_now_add=True)
    date_intervention = models.DateTimeField(null=True, blank=True)
    statut_reparation = models.CharField(max_length=20, choices=[('en_cours', 'En cours'), ('terminee', 'Terminée')])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['panne', 'technicien'], name='unique_affectation')
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['technicien'].queryset = User.objects.filter(role__name='technicien')
        self.fields['panne'].queryset = self.fields['panne'].queryset.filter(status='nouvelle')

    def __str__(self):
        return f'{self.panne.description} - {self.technicien.username} - {self.date_affectation}'


class Notification(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    panne = models.ForeignKey(Panne, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    est_lue = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification ({'Lue' if self.est_lue else 'Non lue'}) pour {self.utilisateur.username} - {self.date_envoi.strftime('%d/%m/%Y %H:%M')}"
