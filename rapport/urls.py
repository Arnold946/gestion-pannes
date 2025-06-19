from django.urls import path

from rapport import views

app_name = 'rapports'

urlpatterns = [
    path('rapport_synthese/', views.rapports_synthese, name='synthese'),
    path('rapport_detaille/', views.rapports_detaille, name='detaille'),
    path('rapport_statistique/',views.rapports_statistique, name='statistique'),
    path('rapport_performance/', views.rapports_performance, name='performance'),
    path('rapport_maintenance/', views.rapports_maintenance, name='maintenance')
]