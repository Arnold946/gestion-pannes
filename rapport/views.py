from datetime import timedelta, datetime, time

from django.core.serializers import json
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Case, When, DurationField, F, Avg, ExpressionWrapper, IntegerField
from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import now, get_current_timezone, make_aware

from pannes.models import Panne, AffectationPanne


# Create your views here.
from django.utils.timezone import now, make_aware
from datetime import datetime, time, timedelta

def rapports_synthese(request):
    periode = request.GET.get('periode', 'day')
    today = now().date()

    if periode == 'day':
        date_debut = today
    elif periode == 'week':
        date_debut = today - timedelta(days=today.weekday())
    elif periode == 'month':
        date_debut = today.replace(day=1)
    elif periode == 'year':
        date_debut = today.replace(month=1, day=1)
    else:
        date_debut = today

    pannes = Panne.objects.filter(date_signalement__date__gte=date_debut)
    total_pannes = pannes.count()

    pannes_resolues = AffectationPanne.objects.filter(panne__in=pannes, statut_reparation="terminee").count()
    pannes_en_cours = AffectationPanne.objects.filter(panne__in=pannes, statut_reparation="en_cours")
    total_en_cours = pannes_en_cours.count()

    try:
        taux_resolution = (pannes_resolues/total_pannes) * 100
    except ZeroDivisionError:
        taux_resolution=0

    context = {
        'total_pannes': total_pannes,
        'pannes_resolues' : pannes_resolues,
        'pannes_en_cours' : pannes_en_cours,
        'taux_resolution' : round(taux_resolution, 2),
        'periode' : periode,
        'total_en_cours' : total_en_cours
    }

    return render(request, 'rapport/rapport_synthese.html', context)


def rapports_detaille(request):
    pannes_par_type = Panne.objects.values('categorie_materiel__name').annotate(nombre=Count('id'))

    total_pannes = Panne.objects.count()
    for stat in pannes_par_type:
        stat['pourcentage'] = round((stat['nombre']/total_pannes) * 100, 1)

    # Statistiques par unité
    pannes_par_unite = (
        Panne.objects.filter(materiel__unite__isnull=False)
        .values('materiel__unite__name')
        .annotate(nombre=Count('id'))
    )

    for stat in pannes_par_unite:
        stat['pourcentage'] = round((stat['nombre'] / total_pannes) * 100, 1)

    # Détails des pannes résolues
    pannes_resolues = AffectationPanne.objects.select_related('panne', 'technicien', 'panne__materiel__categorie') \
        .filter(statut_reparation='terminee', date_reparation__isnull=False)

    context = {
        'pannes_par_type': pannes_par_type,
        'pannes_par_unite': pannes_par_unite,
        'pannes_resolues': pannes_resolues,
    }
    return render(request, 'rapport/rapport_detaille.html', context)

def rapports_statistique(request):
    # Répartition par type de matériel
    pannes_par_type = (
        Panne.objects.filter(materiel__categorie__name__isnull=False)\
        .values('materiel__categorie__name')\
        .annotate(nombre=Count('id'))
    )

    # Répartition par localisation
    pannes_par_unite = (
        Panne.objects.filter(user__unite__name__isnull=False)\
        .values('user__unite__name')
        .annotate(nombre=Count('id'))
    )

    # Préparer les données en listes pour Chart.js
    data_type_materiel = {
        'labels': [item['materiel__categorie__name'] for item in pannes_par_type],
        'data': [item['nombre'] for item in pannes_par_type],
    }

    data_localisation = {
        'labels': [item['user__unite__name'] for item in pannes_par_unite],
        'data': [item['nombre'] for item in pannes_par_unite],
    }

    context = {
        'data_type_materiel': json.dumps(data_type_materiel, cls=DjangoJSONEncoder),
        'data_localisation': json.dumps(data_localisation, cls=DjangoJSONEncoder),
    }
    return render(request, 'rapport/rapport_statistique.html',context)



def rapports_performance(request):
    # Filtrer les pannes terminées avec une date de réparation valide
    pannes_terminees = AffectationPanne.objects.filter(
        statut_reparation='terminee',
        date_reparation__isnull=False,
        date_intervention__isnull=False
    )

    # Calcul du temps moyen de résolution (en heures)
    pannes_terminees = pannes_terminees.annotate(
        duree=ExpressionWrapper(
            F('date_reparation') - F('date_intervention'),
            output_field=DurationField()
        )
    )
    temps_moyen = pannes_terminees.aggregate(moyenne=Avg('duree'))['moyenne']
    temps_moyen_en_heures = round(temps_moyen.total_seconds() / 3600, 1) if temps_moyen else 0

    # Calcul du taux de respect des délais (si durée ≤ 20 heures)
    pannes_terminees = pannes_terminees.annotate(
        respecte=Case(
            When(duree__lte=timedelta(hours=10), then=1),
            default=0,
            output_field=IntegerField()
        )
    )
    respect_delais = pannes_terminees.aggregate(taux=Avg('respecte'))['taux']
    taux_respect = round(respect_delais * 100, 1) if respect_delais is not None else 0

    # Calcul du score de performance (exemple : basé sur temps moyen et taux de respect)
    if temps_moyen_en_heures < 5:
        points_rapidite = 5
    elif temps_moyen_en_heures <= 10:
        points_rapidite = 3
    else:
        points_rapidite = 1

    if taux_respect > 80:
        points_delais = 5
    elif taux_respect >= 50:
        points_delais = 3
    else:
        points_delais = 1

    score = points_rapidite + points_delais

    # Performance par technicien
    techniciens_perf = pannes_terminees.values('technicien__username') \
        .annotate(resolues=Count('id')).order_by('-resolues')

    for tech in techniciens_perf:
        tech['nom'] = tech['technicien__username']
        tech['score'] = min(10, round(tech['resolues'] / 5, 1))  # score basé sur nombre de pannes résolues

    chart_labels = [tech['nom'] for tech in techniciens_perf]
    chart_data = [tech['score'] for tech in techniciens_perf]

    # Envoi des données au template
    context = {
        'temps_moyen': temps_moyen_en_heures,
        'taux_respect': taux_respect,
        'score_performance': score,
        'techniciens_perf': techniciens_perf,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'rapport/rapport_performance.html', context)

def rapports_maintenance(request):
    return render(request, 'rapport/rapport_maintenance.html')