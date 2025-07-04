# Generated by Django 5.2 on 2025-04-27 04:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Panne',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('date_signalement', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('nouvelle', 'Nouvelle'), ('en_cours', 'En cours'), ('resolue', 'Résolue'), ('fermee', 'Fermée')], default='nouvelle', max_length=20)),
                ('priority', models.CharField(choices=[('haute', 'Haute'), ('moyenne', 'Moyenne'), ('basse', 'Basse')], default='moyenne', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='panne_utilisateur', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('est_lue', models.BooleanField(default=False)),
                ('date_envoi', models.DateTimeField(auto_now_add=True)),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('panne', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='pannes.panne')),
            ],
        ),
        migrations.CreateModel(
            name='AffectationPanne',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_affectation', models.DateTimeField(auto_now_add=True)),
                ('date_intervention', models.DateTimeField(blank=True, null=True)),
                ('statut_reparation', models.CharField(choices=[('en_cours', 'En cours'), ('terminee', 'Terminée')], max_length=20)),
                ('attribue_par', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='panne_attribue_par', to=settings.AUTH_USER_MODEL)),
                ('technicien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='panne_technicien', to=settings.AUTH_USER_MODEL)),
                ('panne', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='affectation_panne', to='pannes.panne')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('panne', 'technicien'), name='unique_affectation')],
            },
        ),
    ]
